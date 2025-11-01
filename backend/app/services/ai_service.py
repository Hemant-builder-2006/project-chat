"""
AI Service for Ollama integration.
Handles direct LLM completions and health checks.
"""
import os
import logging
from typing import Optional, Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Ollama configuration from environment
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "llama2")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))


async def get_ollama_completion(
    prompt: str,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get completion from Ollama LLM.
    
    Args:
        prompt: The user prompt/query
        model: Model name (defaults to OLLAMA_DEFAULT_MODEL)
        system_prompt: Optional system message to set context
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens in response
    
    Returns:
        Dict with response text and metadata
    
    Raises:
        Exception if Ollama is not available or request fails
    """
    if model is None:
        model = OLLAMA_DEFAULT_MODEL
    
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            if system_prompt:
                payload["system"] = system_prompt
            
            # Make request to Ollama
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "response": result.get("response", ""),
                "model": result.get("model", model),
                "created_at": result.get("created_at"),
                "done": result.get("done", False),
                "context": result.get("context"),
                "total_duration": result.get("total_duration"),
                "load_duration": result.get("load_duration"),
                "prompt_eval_count": result.get("prompt_eval_count"),
                "eval_count": result.get("eval_count"),
            }
            
    except httpx.TimeoutException:
        logger.error(f"Ollama request timeout after {OLLAMA_TIMEOUT}s")
        raise Exception(f"AI service timeout. The request took longer than {OLLAMA_TIMEOUT} seconds.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"AI service error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Ollama request failed: {str(e)}")
        raise Exception(f"AI service unavailable: {str(e)}")


async def get_ollama_chat_completion(
    messages: list[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """
    Get chat completion from Ollama using chat endpoint.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
                 e.g., [{"role": "user", "content": "Hello"}]
        model: Model name (defaults to OLLAMA_DEFAULT_MODEL)
        temperature: Sampling temperature
    
    Returns:
        Dict with response message and metadata
    """
    if model is None:
        model = OLLAMA_DEFAULT_MODEL
    
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }
            
            response = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "message": result.get("message", {}),
                "model": result.get("model", model),
                "created_at": result.get("created_at"),
                "done": result.get("done", False),
                "total_duration": result.get("total_duration"),
                "eval_count": result.get("eval_count"),
            }
            
    except Exception as e:
        logger.error(f"Ollama chat completion failed: {str(e)}")
        raise Exception(f"AI service unavailable: {str(e)}")


async def check_ollama_health() -> Dict[str, Any]:
    """
    Check if Ollama service is healthy and available.
    
    Returns:
        Dict with health status and available models
    
    Raises:
        Exception if service is unavailable
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check if Ollama is running
            response = await client.get(f"{OLLAMA_HOST}/api/tags")
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            
            return {
                "status": "healthy",
                "host": OLLAMA_HOST,
                "available": True,
                "models": model_names,
                "default_model": OLLAMA_DEFAULT_MODEL,
                "model_count": len(model_names),
            }
            
    except httpx.ConnectError:
        logger.error(f"Cannot connect to Ollama at {OLLAMA_HOST}")
        return {
            "status": "unhealthy",
            "host": OLLAMA_HOST,
            "available": False,
            "error": "Connection refused. Is Ollama running?",
        }
    except Exception as e:
        logger.error(f"Ollama health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "host": OLLAMA_HOST,
            "available": False,
            "error": str(e),
        }


async def pull_model(model_name: str) -> Dict[str, Any]:
    """
    Pull/download a model from Ollama library.
    
    Args:
        model_name: Name of the model to pull (e.g., "llama2", "mistral")
    
    Returns:
        Dict with pull status
    """
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:  # Long timeout for downloads
            response = await client.post(
                f"{OLLAMA_HOST}/api/pull",
                json={"name": model_name}
            )
            
            response.raise_for_status()
            
            return {
                "success": True,
                "model": model_name,
                "message": f"Model {model_name} pulled successfully"
            }
            
    except Exception as e:
        logger.error(f"Failed to pull model {model_name}: {str(e)}")
        return {
            "success": False,
            "model": model_name,
            "error": str(e)
        }


async def list_models() -> list[Dict[str, Any]]:
    """
    List all available models in Ollama.
    
    Returns:
        List of model information dicts
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_HOST}/api/tags")
            response.raise_for_status()
            
            return response.json().get("models", [])
            
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        return []
