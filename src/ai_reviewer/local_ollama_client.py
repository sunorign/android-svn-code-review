from typing import List
from .base_client import BaseAIClient, AIReviewResult, AIReviewFinding
from src.config import Config


class LocalOllamaClient(BaseAIClient):
    """用于AI代码审查的Ollama API客户端实现。"""

    def __init__(self, config: Config):
        """
        初始化Ollama API客户端。

        参数:
            config: 包含Ollama API配置的配置对象
        """
        self.config = config
        self.api_base = config.ollama_api_base or "http://localhost:11434"
        self.default_model = config.ollama_model or "llama3"
        self.max_tokens = config.ollama_max_tokens or 4096
        self.timeout = config.api_timeout or 60

    def review_diff(self, file_path: str, diff_content: str, prompt_template: str) -> AIReviewResult:
        """
        使用Ollama API审查代码差异块。

        参数:
            file_path: 正在审查的文件路径
            diff_content: 要审查的代码差异内容
            prompt_template: 带占位符的提示词模板

        返回:
            包含审查结果或错误信息的AIReviewResult对象
        """
        raise NotImplementedError("Ollama diff review implementation not complete")

    def review_full_file(self, file_path: str, content: str, prompt_template: str) -> AIReviewResult:
        """
        使用Ollama API审查整个文件内容。

        参数:
            file_path: 正在审查的文件路径
            content: 要审查的完整文件内容
            prompt_template: 带占位符的提示词模板

        返回:
            包含审查结果或错误信息的AIReviewResult对象
        """
        raise NotImplementedError("Ollama full file review implementation not complete")
