"""
Groq LLM client implementation.
"""

import os
from typing import Any, Dict, List, Optional

try:
    from groq import Groq
except ImportError:
    Groq = None

from .base import BaseLLMClient
from .config import load_env_file


class GroqClient(BaseLLMClient):
    """Client for Groq API using llama-3.3-70b-versatile model."""
    
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key. If not provided, loads from .env file or GROQ_API_KEY env var.
            model: Model name. Defaults to llama-3.3-70b-versatile.
            base_url: Optional custom base URL for the API.
        """
        if Groq is None:
            raise ImportError(
                "groq package is not installed. Install it with: pip install groq"
            )
        
        # Load .env file if not already loaded
        load_env_file()
        
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Groq API key is required. Provide it as argument or set GROQ_API_KEY env var."
            )
        
        self.model = model or self.DEFAULT_MODEL
        self.client = Groq(api_key=self.api_key, base_url=base_url)
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response from Groq."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming response from Groq."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        
        stream = self.client.chat.completions.create(**params)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a chat response from Groq."""
        # Convert messages to Groq format
        groq_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        params = {
            "model": self.model,
            "messages": groq_messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming chat response from Groq."""
        groq_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        params = {
            "model": self.model,
            "messages": groq_messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        
        stream = self.client.chat.completions.create(**params)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_model_name(self) -> str:
        """Get the Groq model name."""
        return self.model
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "groq"

