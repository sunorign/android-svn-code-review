import os
import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """AI客户端配置。"""
    # Anthropic Claude
    anthropic_api_key: Optional[str] = None
    anthropic_api_url: Optional[str] = None
    anthropic_model: Optional[str] = None
    anthropic_max_tokens: int = 4096

    # OpenRouter
    openrouter_api_key: Optional[str] = None
    openrouter_api_url: Optional[str] = None
    openrouter_model: Optional[str] = None
    openrouter_max_tokens: int = 4096
    openrouter_http_referer: Optional[str] = None

    # Local Ollama
    ollama_api_base: Optional[str] = None
    ollama_model: Optional[str] = None
    ollama_max_tokens: int = 4096

    # Common
    api_timeout: int = 60
    ai_provider: Optional[str] = None

    def has_ai_enabled(self) -> bool:
        """检查是否启用了AI审查。"""
        if not self.ai_provider:
            return False
        match self.ai_provider:
            case 'claude':
                return self.anthropic_api_key is not None and len(self.anthropic_api_key) > 0
            case 'openrouter':
                return self.openrouter_api_key is not None and len(self.openrouter_api_key) > 0
            case 'ollama':
                return self.ollama_api_base is not None
            case _:
                return False

    def get_active_provider(self) -> Optional[str]:
        """获取当前配置的AI提供者。"""
        return self.ai_provider

    @classmethod
    def load_from_env(cls) -> 'Config':
        """从环境变量加载配置（向后兼容）。"""
        return JsonConfigLoader._load_from_env()


class JsonConfigLoader:
    """从JSON文件加载AI客户端配置。"""

    DEFAULT_CONFIG_PATH = os.path.join(
        os.path.dirname(__file__),
        'ai_reviewer',
        'ai_client_config.json'
    )

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> Config:
        """
        从JSON文件加载配置。

        参数:
            config_path: 可选的自定义配置路径，不指定则使用默认路径。

        返回:
            Config 对象

        异常:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置格式错误
        """
        if config_path is None:
            config_path = cls.DEFAULT_CONFIG_PATH

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        config = Config()

        # 加载通用配置
        config.ai_provider = data.get('default_provider')
        config.api_timeout = data.get('api_timeout', 60)

        # 加载各提供者配置
        providers = data.get('providers', {})

        # Claude
        claude_config = providers.get('claude', {})
        config.anthropic_api_key = claude_config.get('api_key')
        config.anthropic_api_url = claude_config.get('api_url')
        config.anthropic_model = claude_config.get('model')
        config.anthropic_max_tokens = claude_config.get('max_tokens', 4096)

        # OpenRouter
        openrouter_config = providers.get('openrouter', {})
        config.openrouter_api_key = openrouter_config.get('api_key')
        config.openrouter_api_url = openrouter_config.get('api_url')
        config.openrouter_model = openrouter_config.get('model')
        config.openrouter_max_tokens = openrouter_config.get('max_tokens', 4096)
        config.openrouter_http_referer = openrouter_config.get('http_referer')

        # Ollama
        ollama_config = providers.get('ollama', {})
        config.ollama_api_base = ollama_config.get('api_base')
        config.ollama_model = ollama_config.get('model')
        config.ollama_max_tokens = ollama_config.get('max_tokens', 4096)

        # 验证必要配置
        if config.ai_provider not in ['claude', 'openrouter', 'ollama', None]:
            raise ValueError(f"未知的AI提供者: {config.ai_provider}")

        return config

    @classmethod
    def load_with_fallback(cls, config_path: Optional[str] = None) -> Config:
        """
        加载配置，尝试JSON，如果失败则回退到环境变量（兼容旧方式）。

        参数:
            config_path: 可选的自定义配置路径

        返回:
            Config 对象
        """
        try:
            return cls.load(config_path)
        except (FileNotFoundError, json.JSONDecodeError):
            # 回退到环境变量读取（兼容旧版）
            return cls._load_from_env()

    @staticmethod
    def _load_from_env() -> Config:
        """从环境变量加载配置（向后兼容）。"""
        # 保留原环境变量读取逻辑用于向后兼容
        from urllib.parse import urlparse

        ollama_api_base = os.environ.get('OLLAMA_API_BASE', 'http://localhost:11434')
        try:
            parsed = urlparse(ollama_api_base)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"OLLAMA_API_BASE的URL格式无效: {ollama_api_base}")
        except Exception as e:
            raise ValueError(f"OLLAMA_API_BASE的URL格式无效: {ollama_api_base}") from e

        default_openrouter_key = "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"

        return Config(
            anthropic_api_key=os.environ.get('ANTHROPIC_API_KEY'),
            anthropic_api_url=os.environ.get('ANTHROPIC_API_URL'),
            anthropic_model=os.environ.get('ANTHROPIC_MODEL'),
            anthropic_max_tokens=int(os.environ.get('ANTHROPIC_MAX_TOKENS', 4096)),
            openrouter_api_key=os.environ.get('OPENROUTER_API_KEY', default_openrouter_key),
            openrouter_api_url=os.environ.get('OPENROUTER_API_URL'),
            openrouter_model=os.environ.get('OPENROUTER_MODEL'),
            openrouter_max_tokens=int(os.environ.get('OPENROUTER_MAX_TOKENS', 4096)),
            openrouter_http_referer=os.environ.get('OPENROUTER_HTTP_REFERER', ''),
            ollama_api_base=ollama_api_base,
            ollama_model=os.environ.get('OLLAMA_MODEL'),
            ollama_max_tokens=int(os.environ.get('OLLAMA_MAX_TOKENS', 4096)),
            api_timeout=int(os.environ.get('API_TIMEOUT', 60)),
            ai_provider=os.environ.get('AI_REVIEW_PROVIDER', 'openrouter'),
        )
