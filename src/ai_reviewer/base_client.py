from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AIReviewFinding:
    file_path: str
    line_start: int
    line_end: int
    issue_type: str  # "BUG", "PERFORMANCE", "STYLE", "SECURITY"
    severity: str  # "BLOCK", "WARNING"
    message: str
    suggestion: Optional[str] = None


@dataclass
class AIReviewResult:
    success: bool
    findings: List[AIReviewFinding]
    error_message: Optional[str] = None
    tokens_used: int = 0


class BaseAIClient(ABC):
    """Base class for AI review clients."""

    @abstractmethod
    def review_diff(self, file_path: str, diff_content: str, prompt_template: str) -> AIReviewResult:
        """Review a diff chunk with AI."""
        raise NotImplementedError()

    @abstractmethod
    def review_full_file(self, file_path: str, content: str, prompt_template: str) -> AIReviewResult:
        """Review the full file with AI."""
        raise NotImplementedError()
