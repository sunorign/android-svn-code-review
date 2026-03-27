from typing import List
from .base_client import BaseAIClient, AIReviewResult, AIReviewFinding
from src.config import Config


class LocalOllamaClient(BaseAIClient):
    """Ollama API client implementation for AI review."""

    def __init__(self, config: Config):
        """
        Initialize the Ollama API client.

        Args:
            config: Configuration object containing Ollama API configuration
        """
        self.config = config
        self.api_base = config.ollama_api_base or "http://localhost:11434"
        self.default_model = config.ollama_model or "llama3"
        self.max_tokens = config.ollama_max_tokens or 4096
        self.timeout = config.api_timeout or 60

    def review_diff(self, file_path: str, diff_content: str, prompt_template: str) -> AIReviewResult:
        """
        Review a diff chunk using Ollama API.

        Args:
            file_path: Path to the file being reviewed
            diff_content: Diff content to review
            prompt_template: Prompt template with placeholders

        Returns:
            AIReviewResult containing findings or error
        """
        raise NotImplementedError("Ollama diff review implementation not complete")

    def review_full_file(self, file_path: str, content: str, prompt_template: str) -> AIReviewResult:
        """
        Review a full file using Ollama API.

        Args:
            file_path: Path to the file being reviewed
            content: Full file content to review
            prompt_template: Prompt template with placeholders

        Returns:
            AIReviewResult containing findings or error
        """
        raise NotImplementedError("Ollama full file review implementation not complete")
