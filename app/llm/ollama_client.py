"""
Ollama LLM client implementation.
"""

import os
from typing import Any, Dict, List, Optional

import requests

from .base import BaseLLMClient
from .config import load_env_file


class OllamaClient(BaseLLMClient):
    """Client for Ollama API using gemma3:1b model."""
    
    DEFAULT_MODEL = "gemma3:1b"
    DEFAULT_BASE_URL = "http://localhost:11434"
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL. If not provided, loads from .env file or OLLAMA_BASE_URL env var.
                     Defaults to http://localhost:11434.
            model: Model name. Defaults to gemma3:1b.
        """
        # Load .env file if not already loaded
        load_env_file()
        
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", self.DEFAULT_BASE_URL)
        self.model = model or self.DEFAULT_MODEL
        
        # Remove trailing slash if present
        self.base_url = self.base_url.rstrip('/')
    
    def _check_model_available(self) -> bool:
        """Check if the model is available in Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                return self.model in model_names
        except Exception:
            pass
        return False
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response from Ollama."""
        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                **kwargs.get("options", {})
            }
        }
        
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=kwargs.get("timeout", 300)
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming response from Ollama."""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                **kwargs.get("options", {})
            }
        }
        
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            stream=True,
            timeout=kwargs.get("timeout", 300)
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                import json
                chunk = json.loads(line)
                if "response" in chunk:
                    yield chunk["response"]
                if chunk.get("done", False):
                    break
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a chat response from Ollama."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                **kwargs.get("options", {})
            }
        }
        
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=kwargs.get("timeout", 300)
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get("message", {}).get("content", "")
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming chat response from Ollama."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                **kwargs.get("options", {})
            }
        }
        
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=kwargs.get("timeout", 300)
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                import json
                chunk = json.loads(line)
                if "message" in chunk and "content" in chunk["message"]:
                    yield chunk["message"]["content"]
                if chunk.get("done", False):
                    break
    
    def get_model_name(self) -> str:
        """Get the Ollama model name."""
        return self.model
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "ollama"

