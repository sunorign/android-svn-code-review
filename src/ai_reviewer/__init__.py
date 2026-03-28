import importlib
import logging
from typing import List, Optional

from src.config import Config
from src.ai_reviewer.base_client import BaseAIClient, AIReviewResult, AIReviewFinding
from src.ai_reviewer.claude_client import ClaudeClient
from src.ai_reviewer.openrouter_client import OpenRouterClient
from src.ai_reviewer.local_ollama_client import LocalOllamaClient


logger = logging.getLogger(__name__)


def get_ai_client(config: Config) -> Optional[BaseAIClient]:
    """Factory method to get the configured AI client."""
    provider = config.ai_provider
    if not provider:
        return None

    match provider:
        case 'claude':
            return ClaudeClient(config)
        case 'openrouter':
            return OpenRouterClient(config)
        case 'ollama':
            return LocalOllamaClient(config)
        case _:
            logger.warning(f"Unknown AI provider: {provider}")
            return None

__all__ = [
    'BaseAIClient',
    'AIReviewFinding',
    'AIReviewResult',
    'get_ai_client',
]
