"""
LLM client module for unified access to different LLM providers.

Supports:
- Groq (using llama-3.3-70b-versatile)
- Ollama (using gemma3:1b)
"""

# Load environment variables from .env file
from . import config  # noqa: F401

from .base import BaseLLMClient
from .groq_client import GroqClient
from .ollama_client import OllamaClient
from .unified_client import UnifiedLLMClient, get_llm_client

__all__ = [
    'BaseLLMClient',
    'GroqClient',
    'OllamaClient',
    'UnifiedLLMClient',
    'get_llm_client',
]

