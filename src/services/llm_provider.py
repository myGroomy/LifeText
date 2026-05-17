"""
LLM Provider abstraction - supports multiple AI models.

Supported providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- DeepSeek
- Any OpenAI-compatible API
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ) -> str:
        """
        Generate completion from LLM.
        
        Args:
            system_prompt: System instructions
            user_prompt: User message
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI provider with model: {model}")
    
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Anthropic provider with model: {model}")
    
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ) -> str:
        response = self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.content[0].text


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=None  # Set per request
        )
        self.model_name = model
        logger.info(f"Initialized Gemini provider with model: {model}")
    
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ) -> str:
        # Gemini combines system + user prompt
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        response = self.model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        return response.text


class DeepSeekProvider(LLMProvider):
    """DeepSeek provider (OpenAI-compatible API)."""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model
        logger.info(f"Initialized DeepSeek provider with model: {model}")
    
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content


class OpenAICompatibleProvider(LLMProvider):
    """Generic OpenAI-compatible API provider (Ollama, LM Studio, etc)."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str
    ):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        logger.info(f"Initialized OpenAI-compatible provider: {base_url} with model: {model}")
    
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content


def get_llm_provider(
    provider_name: str,
    api_key: str,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> LLMProvider:
    """
    Factory function to get LLM provider.
    
    Args:
        provider_name: "openai", "anthropic", "gemini", "deepseek", "openai-compatible"
        api_key: API key for the provider
        model: Model name (optional, uses default if not provided)
        base_url: Base URL for OpenAI-compatible providers
        
    Returns:
        LLMProvider instance
        
    Examples:
        # OpenAI
        provider = get_llm_provider("openai", api_key, model="gpt-4")
        
        # Claude
        provider = get_llm_provider("anthropic", api_key, model="claude-sonnet-4-20250514")
        
        # Gemini
        provider = get_llm_provider("gemini", api_key, model="gemini-2.0-flash-exp")
        
        # DeepSeek
        provider = get_llm_provider("deepseek", api_key)
        
        # Ollama (local)
        provider = get_llm_provider(
            "openai-compatible",
            api_key="ollama",
            model="llama3",
            base_url="http://localhost:11434/v1"
        )
    """
    provider_name = provider_name.lower()
    
    if provider_name == "openai":
        return OpenAIProvider(api_key, model or "gpt-4")
    
    elif provider_name == "anthropic":
        return AnthropicProvider(api_key, model or "claude-sonnet-4-20250514")
    
    elif provider_name == "gemini":
        return GeminiProvider(api_key, model or "gemini-2.0-flash-exp")
    
    elif provider_name == "deepseek":
        return DeepSeekProvider(api_key, model or "deepseek-chat")
    
    elif provider_name == "openai-compatible":
        if not base_url:
            raise ValueError("base_url required for openai-compatible provider")
        if not model:
            raise ValueError("model required for openai-compatible provider")
        return OpenAICompatibleProvider(api_key, base_url, model)
    
    else:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Supported: openai, anthropic, gemini, deepseek, openai-compatible"
        )


def load_prompt(prompt_name: str) -> str:
    """
    Load prompt from prompts/ directory.
    
    Args:
        prompt_name: Name without extension (e.g., "system_transcription")
        
    Returns:
        Prompt text
    """
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / f"{prompt_name}.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")
