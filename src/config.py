import os
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class Config:
    anthropic_api_key: Optional[str]
    anthropic_api_url: Optional[str]
    anthropic_model: Optional[str]
    anthropic_max_tokens: Optional[int]
    openrouter_api_key: Optional[str]
    openrouter_api_url: Optional[str]
    openrouter_model: Optional[str]
    openrouter_max_tokens: Optional[int]
    ollama_api_base: Optional[str]
    ollama_model: Optional[str]
    ollama_max_tokens: Optional[int]
    api_timeout: Optional[int]
    ai_provider: Optional[str]  # "claude", "openrouter", "ollama"

    @classmethod
    def load_from_env(cls) -> 'Config':
        # Get ollama_api_base from environment, default to http://localhost:11434 if not set
        ollama_api_base = os.environ.get('OLLAMA_API_BASE', 'http://localhost:11434')

        # Validate ollama_api_base is a valid URL
        try:
            result = urlparse(ollama_api_base)
            if not all([result.scheme, result.netloc]):
                raise ValueError(f"Invalid URL format for OLLAMA_API_BASE: {ollama_api_base}")
        except Exception as e:
            raise ValueError(f"Invalid URL format for OLLAMA_API_BASE: {ollama_api_base}") from e

        return cls(
            anthropic_api_key=os.environ.get('ANTHROPIC_API_KEY'),
            anthropic_api_url=os.environ.get('ANTHROPIC_API_URL'),
            anthropic_model=os.environ.get('ANTHROPIC_MODEL'),
            anthropic_max_tokens=int(os.environ.get('ANTHROPIC_MAX_TOKENS', 4096)),
            openrouter_api_key=os.environ.get('OPENROUTER_API_KEY'),
            openrouter_api_url=os.environ.get('OPENROUTER_API_URL'),
            openrouter_model=os.environ.get('OPENROUTER_MODEL'),
            openrouter_max_tokens=int(os.environ.get('OPENROUTER_MAX_TOKENS', 4096)),
            ollama_api_base=ollama_api_base,
            ollama_model=os.environ.get('OLLAMA_MODEL'),
            ollama_max_tokens=int(os.environ.get('OLLAMA_MAX_TOKENS', 4096)),
            api_timeout=int(os.environ.get('API_TIMEOUT', 60)),
            ai_provider=os.environ.get('AI_REVIEW_PROVIDER'),
        )

    def has_ai_enabled(self) -> bool:
        """Check if any AI provider is configured."""
        if self.ai_provider == 'claude' and self.anthropic_api_key:
            return True
        if self.ai_provider == 'openrouter' and self.openrouter_api_key:
            return True
        if self.ai_provider == 'ollama' and self.ollama_api_base:
            return True
        # Auto-detect if any is available (only consider explicitly configured providers, not default ollama)
        if self.anthropic_api_key:
            return True
        if self.openrouter_api_key:
            return True
        # Only consider ollama available if it's explicitly configured with a custom URL
        if self.ollama_api_base and self.ollama_api_base != 'http://localhost:11434':
            return True
        return False

    def get_active_provider(self) -> Optional[str]:
        """Get the active AI provider."""
        if self.ai_provider:
            return self.ai_provider
        if self.anthropic_api_key:
            return 'claude'
        if self.openrouter_api_key:
            return 'openrouter'
        # Only consider ollama as active if it's explicitly configured with a custom URL
        if self.ollama_api_base and self.ollama_api_base != 'http://localhost:11434':
            return 'ollama'
        return None