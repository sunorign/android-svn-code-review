from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AIReviewFinding:
    file_path: str
    line_start: int
    line_end: int
    issue_type: str  # "缺陷", "性能", "风格", "安全"
    severity: str  # "阻断", "警告"
    message: str
    suggestion: Optional[str] = None


@dataclass
class AIReviewResult:
    success: bool
    findings: List[AIReviewFinding]
    error_message: Optional[str] = None
    tokens_used: int = 0


class BaseAIClient(ABC):
    """AI审查客户端的基类。"""

    @abstractmethod
    def review_diff(self, file_path: str, diff_content: str, prompt_template: str) -> AIReviewResult:
        """使用AI审查代码差异块。"""
        raise NotImplementedError()

    @abstractmethod
    def review_full_file(self, file_path: str, content: str, prompt_template: str) -> AIReviewResult:
        """使用AI审查完整文件。"""
        raise NotImplementedError()