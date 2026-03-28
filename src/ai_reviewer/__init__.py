import logging
from typing import Optional

from src.config import Config, JsonConfigLoader
from src.ai_reviewer.base_client import BaseAIClient, AIReviewFinding, AIReviewResult
from src.ai_reviewer.claude_client import ClaudeClient
from src.ai_reviewer.openrouter_client import OpenRouterClient
from src.ai_reviewer.local_ollama_client import LocalOllamaClient

logger = logging.getLogger(__name__)


def get_ai_client(config: Optional[Config] = None) -> Optional[BaseAIClient]:
    """Factory method to get the configured AI client.

    Args:
        config: Optional configuration object. If not provided, it will be loaded using
                JsonConfigLoader.load_with_fallback() which falls back to environment variables
                if the JSON config file is missing or invalid.

    Returns:
        An instance of the configured AI client, or None if no valid provider is configured.
    """
    if config is None:
        config = JsonConfigLoader.load_with_fallback()

    provider = config.get_active_provider()
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