"""
RAG (Retrieval Augmented Generation) Service.
Handles document ingestion, embeddings, and semantic search with ChromaDB.
"""
import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import PyPDF2
import io
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration from environment
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Global embedding model instance (loaded once)
_embedding_model = None


def get_embeddings() -> SentenceTransformer:
    """
    Get or initialize the sentence transformer embedding model.
    
    Returns:
        SentenceTransformer model instance
    """
    global _embedding_model
    
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
    
    return _embedding_model


def get_chroma_client() -> chromadb.HttpClient:
    """
    Get ChromaDB client connection.
    
    Returns:
        ChromaDB HttpClient instance
    """
    try:
        client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            settings=Settings(
                anonymized_telemetry=False,
            )
        )
        
        # Test connection
        client.heartbeat()
        
        return client
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB: {str(e)}")
        raise Exception(f"ChromaDB connection failed: {str(e)}")


async def check_chromadb_health() -> Dict[str, Any]:
    """
    Check if ChromaDB is healthy and accessible.
    
    Returns:
        Dict with health status
    """
    try:
        client = get_chroma_client()
        heartbeat = client.heartbeat()
        collections = client.list_collections()
        
        return {
            "status": "healthy",
            "host": f"{CHROMA_HOST}:{CHROMA_PORT}",
            "available": True,
            "heartbeat": heartbeat,
            "collections": [c.name for c in collections],
            "collection_count": len(collections),
        }
    except Exception as e:
        logger.error(f"ChromaDB health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "host": f"{CHROMA_HOST}:{CHROMA_PORT}",
            "available": False,
            "error": str(e),
        }


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text content from PDF file.
    
    Args:
        file_content: PDF file bytes
    
    Returns:
        Extracted text as string
    """
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract PDF text: {str(e)}")
        raise Exception(f"PDF extraction failed: {str(e)}")


def split_text_into_chunks(text: str) -> List[str]:
    """
    Split text into smaller chunks for embedding.
    
    Args:
        text: Full text to split
    
    Returns:
        List of text chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    return chunks


async def ingest_document(
    file_content: bytes,
    filename: str,
    channel_id: str,
    user_id: str,
    content_type: str = "application/pdf"
) -> Dict[str, Any]:
    """
    Ingest a document into ChromaDB for RAG.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        channel_id: Channel ID for filtering
        user_id: User who uploaded
        content_type: MIME type
    
    Returns:
        Dict with ingestion stats
    """
    try:
        # Extract text based on file type
        if content_type == "application/pdf":
            text = extract_text_from_pdf(file_content)
        elif content_type in ["text/plain", "text/markdown"]:
            text = file_content.decode("utf-8")
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        if not text or len(text.strip()) < 10:
            raise ValueError("Document contains no extractable text")
        
        # Split into chunks
        chunks = split_text_into_chunks(text)
        logger.info(f"Split document into {len(chunks)} chunks")
        
        # Get embedding model
        embedding_model = get_embeddings()
        
        # Generate embeddings for all chunks
        embeddings = embedding_model.encode(chunks).tolist()
        
        # Connect to ChromaDB
        client = get_chroma_client()
        
        # Get or create collection
        collection_name = "documents"
        try:
            collection = client.get_collection(name=collection_name)
        except:
            collection = client.create_collection(
                name=collection_name,
                metadata={"description": "Document embeddings for RAG"}
            )
        
        # Prepare document IDs and metadata
        doc_ids = [f"{channel_id}_{filename}_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "channel_id": channel_id,
                "filename": filename,
                "user_id": user_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "content_type": content_type,
            }
            for i in range(len(chunks))
        ]
        
        # Add documents to collection
        collection.add(
            ids=doc_ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully ingested document: {filename}")
        
        return {
            "success": True,
            "filename": filename,
            "chunks": len(chunks),
            "total_characters": len(text),
            "collection": collection_name,
        }
        
    except Exception as e:
        logger.error(f"Document ingestion failed: {str(e)}")
        raise Exception(f"Failed to ingest document: {str(e)}")


async def ingest_chat_message(
    message_content: str,
    message_id: str,
    channel_id: str,
    user_id: str,
) -> Dict[str, Any]:
    """
    Ingest a chat message into ChromaDB for context search.
    
    Args:
        message_content: Message text
        message_id: Message ID
        channel_id: Channel ID
        user_id: User ID who sent message
    
    Returns:
        Dict with ingestion status
    """
    try:
        # Skip very short messages
        if len(message_content.strip()) < 20:
            return {"success": False, "reason": "Message too short"}
        
        # Get embedding model
        embedding_model = get_embeddings()
        
        # Generate embedding
        embedding = embedding_model.encode([message_content])[0].tolist()
        
        # Connect to ChromaDB
        client = get_chroma_client()
        
        # Get or create messages collection
        collection_name = "messages"
        try:
            collection = client.get_collection(name=collection_name)
        except:
            collection = client.create_collection(
                name=collection_name,
                metadata={"description": "Chat message embeddings"}
            )
        
        # Add message
        collection.add(
            ids=[message_id],
            documents=[message_content],
            embeddings=[embedding],
            metadatas=[{
                "channel_id": channel_id,
                "user_id": user_id,
                "type": "message",
            }]
        )
        
        return {
            "success": True,
            "message_id": message_id,
            "collection": collection_name,
        }
        
    except Exception as e:
        logger.error(f"Message ingestion failed: {str(e)}")
        return {"success": False, "error": str(e)}


async def perform_rag_search(
    query: str,
    accessible_channel_ids: List[str],
    n_results: int = 5,
    collection_name: str = "documents"
) -> Dict[str, Any]:
    """
    Perform RAG search: retrieve relevant documents and generate response.
    
    Args:
        query: User's search query
        accessible_channel_ids: List of channel IDs user can access
        n_results: Number of results to retrieve
        collection_name: ChromaDB collection to search
    
    Returns:
        Dict with search results and context
    """
    try:
        # Get embedding model
        embedding_model = get_embeddings()
        
        # Generate query embedding
        query_embedding = embedding_model.encode([query])[0].tolist()
        
        # Connect to ChromaDB
        client = get_chroma_client()
        
        try:
            collection = client.get_collection(name=collection_name)
        except:
            return {
                "results": [],
                "context": "",
                "message": f"Collection '{collection_name}' not found. No documents have been uploaded yet."
            }
        
        # Build where filter for accessible channels
        where_filter = None
        if accessible_channel_ids:
            if len(accessible_channel_ids) == 1:
                where_filter = {"channel_id": accessible_channel_ids[0]}
            else:
                where_filter = {"channel_id": {"$in": accessible_channel_ids}}
        
        # Search for similar documents
        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        results = []
        context_pieces = []
        
        if search_results["documents"] and len(search_results["documents"][0]) > 0:
            for i, doc in enumerate(search_results["documents"][0]):
                metadata = search_results["metadatas"][0][i] if search_results["metadatas"] else {}
                distance = search_results["distances"][0][i] if search_results["distances"] else None
                
                results.append({
                    "document": doc,
                    "metadata": metadata,
                    "distance": distance,
                    "relevance_score": 1.0 - (distance or 0.0) if distance is not None else None
                })
                
                context_pieces.append(doc)
        
        # Combine context
        context = "\n\n".join(context_pieces)
        
        return {
            "query": query,
            "results": results,
            "context": context,
            "result_count": len(results),
        }
        
    except Exception as e:
        logger.error(f"RAG search failed: {str(e)}")
        raise Exception(f"Search failed: {str(e)}")


async def delete_channel_documents(channel_id: str) -> Dict[str, Any]:
    """
    Delete all documents associated with a channel.
    
    Args:
        channel_id: Channel ID
    
    Returns:
        Dict with deletion status
    """
    try:
        client = get_chroma_client()
        
        for collection_name in ["documents", "messages"]:
            try:
                collection = client.get_collection(name=collection_name)
                
                # Get all document IDs for this channel
                results = collection.get(
                    where={"channel_id": channel_id},
                    include=[]
                )
                
                if results["ids"]:
                    collection.delete(ids=results["ids"])
                    logger.info(f"Deleted {len(results['ids'])} documents from {collection_name} for channel {channel_id}")
            except:
                pass  # Collection might not exist
        
        return {
            "success": True,
            "channel_id": channel_id,
        }
        
    except Exception as e:
        logger.error(f"Failed to delete channel documents: {str(e)}")
        return {"success": False, "error": str(e)}
