"""
AI-powered endpoints for search, summarization, and document Q&A.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.channel import Channel
from app.models.membership import Membership
from app.models.message import Message
from app.services.ai_service import (
    get_ollama_completion,
    get_ollama_chat_completion,
    check_ollama_health,
    list_models,
)
from app.services.rag_service import (
    perform_rag_search,
    ingest_document,
    check_chromadb_health,
    ingest_chat_message,
)

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)


# Schemas
class AISearchRequest(BaseModel):
    """Request schema for AI-powered search."""
    query: str = Field(..., min_length=1, max_length=500)
    channel_ids: Optional[List[str]] = None
    n_results: int = Field(default=5, ge=1, le=20)


class AISearchResponse(BaseModel):
    """Response schema for AI search."""
    query: str
    answer: str
    context: str
    sources: List[dict]
    result_count: int


class SummarizeRequest(BaseModel):
    """Request schema for channel summarization."""
    message_limit: int = Field(default=50, ge=10, le=200)
    summary_type: str = Field(default="concise", pattern="^(concise|detailed|bullet)$")


class ChatRequest(BaseModel):
    """Request schema for direct AI chat."""
    message: str = Field(..., min_length=1, max_length=2000)
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    """Response schema for AI chat."""
    response: str
    model: str


# Helper function to get accessible channels
async def get_user_accessible_channels(
    user: User,
    db: AsyncSession,
    channel_ids: Optional[List[str]] = None
) -> List[str]:
    """
    Get list of channel IDs the user has access to.
    
    Args:
        user: Current user
        db: Database session
        channel_ids: Optional filter to specific channels
    
    Returns:
        List of channel IDs
    """
    # Get all groups user is a member of
    result = await db.execute(
        select(Membership.group_id).where(Membership.user_id == user.id)
    )
    user_group_ids = [row[0] for row in result.all()]
    
    # Get channels in those groups
    query = select(Channel.id).where(Channel.group_id.in_(user_group_ids))
    
    if channel_ids:
        query = query.where(Channel.id.in_(channel_ids))
    
    result = await db.execute(query)
    return [row[0] for row in result.all()]


@router.post("/search", response_model=AISearchResponse)
async def ai_search(
    request: AISearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform AI-powered semantic search across documents.
    
    - Searches through uploaded documents in accessible channels
    - Uses RAG (Retrieval Augmented Generation) for context-aware answers
    - Returns relevant sources and generated response
    """
    try:
        # Get accessible channels
        accessible_channels = await get_user_accessible_channels(
            current_user, db, request.channel_ids
        )
        
        if not accessible_channels:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No accessible channels to search"
            )
        
        # Perform RAG search
        search_results = await perform_rag_search(
            query=request.query,
            accessible_channel_ids=accessible_channels,
            n_results=request.n_results
        )
        
        # If no results, return early
        if not search_results["results"]:
            return AISearchResponse(
                query=request.query,
                answer="I couldn't find any relevant documents to answer your question. Try uploading documents first or rephrasing your query.",
                context="",
                sources=[],
                result_count=0
            )
        
        # Generate AI response using context
        context = search_results["context"]
        prompt = f"""Based on the following context from documents, answer the user's question.
If the answer is not in the context, say so.

Context:
{context}

Question: {request.query}

Answer:"""
        
        ai_response = await get_ollama_completion(
            prompt=prompt,
            system_prompt="You are a helpful assistant that answers questions based on provided context. Be concise and accurate."
        )
        
        return AISearchResponse(
            query=request.query,
            answer=ai_response["response"],
            context=context[:1000],  # Limit context in response
            sources=search_results["results"],
            result_count=search_results["result_count"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/summarize/{channel_id}")
async def summarize_channel(
    channel_id: str,
    request: SummarizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI summary of recent channel messages.
    
    - Summarizes recent conversation in a channel
    - Supports different summary styles (concise, detailed, bullet points)
    - Requires channel access
    """
    # Verify channel access
    accessible_channels = await get_user_accessible_channels(
        current_user, db, [channel_id]
    )
    
    if channel_id not in accessible_channels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this channel"
        )
    
    try:
        # Fetch recent messages
        result = await db.execute(
            select(Message)
            .where(Message.channel_id == channel_id)
            .order_by(Message.created_at.desc())
            .limit(request.message_limit)
        )
        messages = result.scalars().all()
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No messages found in channel"
            )
        
        # Format messages for context
        message_texts = []
        for msg in reversed(messages):  # Chronological order
            message_texts.append(f"User: {msg.content}")
        
        context = "\n".join(message_texts)
        
        # Create summary prompt based on type
        if request.summary_type == "bullet":
            prompt_instruction = "Provide a bullet-point summary of the key points discussed."
        elif request.summary_type == "detailed":
            prompt_instruction = "Provide a detailed summary covering all major topics and conclusions."
        else:  # concise
            prompt_instruction = "Provide a concise summary of the main discussion points."
        
        prompt = f"""Summarize the following conversation.

{prompt_instruction}

Conversation:
{context}

Summary:"""
        
        ai_response = await get_ollama_completion(
            prompt=prompt,
            system_prompt="You are a helpful assistant that creates accurate summaries of conversations."
        )
        
        return {
            "channel_id": channel_id,
            "message_count": len(messages),
            "summary_type": request.summary_type,
            "summary": ai_response["response"],
            "model": ai_response["model"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}"
        )


@router.post("/upload/{channel_id}")
async def upload_document_for_rag(
    channel_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and ingest a document for AI search.
    
    - Uploads document (PDF, TXT, MD)
    - Extracts text and creates embeddings
    - Makes document searchable via AI search
    """
    # Verify channel access
    accessible_channels = await get_user_accessible_channels(
        current_user, db, [channel_id]
    )
    
    if channel_id not in accessible_channels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this channel"
        )
    
    # Validate file type
    allowed_types = ["application/pdf", "text/plain", "text/markdown"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: PDF, TXT, MD"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        # Ingest document
        result = await ingest_document(
            file_content=file_content,
            filename=file.filename,
            channel_id=channel_id,
            user_id=current_user.id,
            content_type=file.content_type
        )
        
        return {
            "message": "Document uploaded and indexed successfully",
            "filename": file.filename,
            "channel_id": channel_id,
            "stats": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Direct AI chat completion (no RAG context).
    
    - Send a message to the AI and get a response
    - Optionally customize system prompt and temperature
    - Choose different models if available
    """
    try:
        ai_response = await get_ollama_completion(
            prompt=request.message,
            system_prompt=request.system_prompt,
            model=request.model,
            temperature=request.temperature
        )
        
        return ChatResponse(
            response=ai_response["response"],
            model=ai_response["model"]
        )
        
    except Exception as e:
        logger.error(f"AI chat failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )


@router.get("/health")
async def ai_health_check():
    """
    Check health status of AI services (Ollama and ChromaDB).
    
    Returns status of both services and available models.
    """
    ollama_health = await check_ollama_health()
    chroma_health = await check_chromadb_health()
    
    overall_healthy = (
        ollama_health.get("available", False) and
        chroma_health.get("available", False)
    )
    
    return {
        "status": "healthy" if overall_healthy else "degraded",
        "services": {
            "ollama": ollama_health,
            "chromadb": chroma_health
        }
    }


@router.get("/models")
async def list_available_models(
    current_user: User = Depends(get_current_user)
):
    """
    List all available AI models in Ollama.
    
    Returns list of models with metadata.
    """
    try:
        models = await list_models()
        return {
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve models"
        )
