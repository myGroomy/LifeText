"""In-app chat assistant endpoint."""
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from src.services.llm_provider import get_llm_provider, load_prompt
from src.config import get_settings

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)
settings = get_settings()


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str


class ChatResponse(BaseModel):
    """Chat response schema."""
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    In-app AI assistant for LifeText help.
    
    Scope: Only answers questions about LifeText features.
    Does NOT transcribe audio or answer off-topic questions.
    """
    # Load system prompt
    system_prompt = load_prompt("system_qa_chat")
    
    # Get LLM provider
    provider = get_llm_provider(
        provider_name=settings.llm_provider,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url
    )
    
    logger.info(f"Chat request: {request.message[:50]}...")
    
    # Generate response
    response = provider.complete(
        system_prompt=system_prompt,
        user_prompt=request.message,
        temperature=0.3,  # Slightly higher for conversational tone
        max_tokens=1024
    )
    
    return ChatResponse(response=response.strip())
