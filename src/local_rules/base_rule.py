import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from src.diff_parser import DiffChange, FileDiff


@dataclass
class RuleFinding:
    """Represents an issue found by a rule."""
    file_path: str
    line_number: int
    rule_name: str
    message: str
    severity: str  # "BLOCK" or "WARNING"
    code_snippet: Optional[str] = None

    def is_blocking(self) -> bool:
        return self.severity.upper() == "BLOCK"


class BaseRule(ABC):
    """Base class for all local review rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Rule name displayed in reports."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of what the rule checks."""
        pass

    @abstractmethod
    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        """Check a single changed line in a diff.

        Args:
            file_diff: The entire file diff
            change: The specific changed line to check

        Returns:
            List of findings (empty if no issues)
        """
        pass

    @abstractmethod
    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        """Check the entire file content (for full review mode).

        Args:
            file_path: Path to the file
            content: Full content of the file

        Returns:
            List of findings (empty if no issues)
        """
        pass

    def _is_pattern_in_string(self, line: str, match_start: int, match_end: int) -> bool:
        """Check if the matched pattern is inside a string literal."""
        in_quote = False
        i = 0
        while i < len(line):
            if i < match_start:
                if line[i] == '"' and (i == 0 or line[i-1] != '\\'):
                    in_quote = not in_quote
            elif match_start <= i < match_end:
                pass
            else:
                break
            i += 1

        return in_quote

    def _is_line_comment(self, line: str) -> bool:
        """Check if line is a single-line comment."""
        stripped = line.strip()
        return stripped.startswith('//') or stripped.startswith('/*')

    def _remove_comments(self, content: str) -> str:
        """Remove comments from content to avoid matching in comments."""
        # Handle /* ... */ comments (including unclosed at end of line)
        if '/*' in content:
            start_idx = content.find('/*')
            end_idx = content.find('*/', start_idx)
            if end_idx != -1:
                # Remove closed comment block
                content = content[:start_idx] + content[end_idx + 2:]
            else:
                # Remove everything from /* to end of line
                content = content[:start_idx]

        # Remove // comments
        content = re.sub(r'//.*$', '', content)
        return content