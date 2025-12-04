"""
Unified LLM client that can switch between different providers.
"""

import os
from typing import Any, Dict, List, Optional, Literal

from .base import BaseLLMClient
from .groq_client import GroqClient
from .ollama_client import OllamaClient
from .config import load_env_file


class UnifiedLLMClient(BaseLLMClient):
    """
    Unified LLM client that provides a single interface to switch between providers.
    
    Supports:
    - groq: Uses llama-3.3-70b-versatile model
    - ollama: Uses gemma3:1b model
    """
    
    def __init__(
        self,
        provider: Literal["groq", "ollama"] = "groq",
        groq_api_key: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize unified LLM client.
        
        Args:
            provider: Which provider to use ('groq' or 'ollama'). 
                     If not specified, loads from .env file or LLM_PROVIDER env var.
                     Defaults to 'groq'.
            groq_api_key: Groq API key (or loads from .env file or GROQ_API_KEY env var)
            ollama_base_url: Ollama base URL (or loads from .env file or OLLAMA_BASE_URL env var)
            model: Optional model override (provider-specific)
        """
        # Load .env file if not already loaded
        load_env_file()
        
        # Get provider from env var if not specified
        if provider is None:
            provider = os.getenv("LLM_PROVIDER", "groq").lower()
        
        self.provider = provider.lower()
        
        if self.provider == "groq":
            self.client = GroqClient(api_key=groq_api_key, model=model)
        elif self.provider == "ollama":
            self.client = OllamaClient(base_url=ollama_base_url, model=model)
        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: 'groq', 'ollama'"
            )
    
    def switch_provider(
        self,
        provider: Literal["groq", "ollama"],
        groq_api_key: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        model: Optional[str] = None
    ) -> None:
        """
        Switch to a different provider.
        
        Args:
            provider: Provider to switch to ('groq' or 'ollama')
            groq_api_key: Groq API key (if switching to groq)
            ollama_base_url: Ollama base URL (if switching to ollama)
            model: Optional model override
        """
        self.provider = provider.lower()
        
        if self.provider == "groq":
            self.client = GroqClient(api_key=groq_api_key, model=model)
        elif self.provider == "ollama":
            self.client = OllamaClient(base_url=ollama_base_url, model=model)
        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: 'groq', 'ollama'"
            )
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response using the current provider."""
        return self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming response using the current provider."""
        return self.client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a chat response using the current provider."""
        return self.client.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming chat response using the current provider."""
        return self.client.chat_stream(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def get_model_name(self) -> str:
        """Get the current model name."""
        return self.client.get_model_name()
    
    def get_provider_name(self) -> str:
        """Get the current provider name."""
        return self.provider
    
    def get_current_client(self) -> BaseLLMClient:
        """
        Get the underlying client instance.
        
        Returns:
            The current provider's client instance
        """
        return self.client


def get_llm_client(
    provider: Optional[Literal["groq", "ollama"]] = None,
    **kwargs
) -> UnifiedLLMClient:
    """
    Convenience function to get a unified LLM client.
    
    Args:
        provider: Provider to use ('groq' or 'ollama'). 
                If not specified, loads from .env file or LLM_PROVIDER env var.
                Defaults to 'groq'.
        **kwargs: Additional arguments passed to UnifiedLLMClient
    
    Returns:
        UnifiedLLMClient instance
    
    Example:
        >>> client = get_llm_client(provider="groq")
        >>> response = client.generate("Hello!")
        >>> 
        >>> # Switch to Ollama
        >>> client.switch_provider("ollama")
        >>> response = client.generate("Hello!")
    """
    # Load .env file if not already loaded
    load_env_file()
    
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "groq").lower()
    
    return UnifiedLLMClient(provider=provider, **kwargs)

