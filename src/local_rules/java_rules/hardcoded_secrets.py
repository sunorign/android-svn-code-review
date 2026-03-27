import re
from typing import List, Tuple, Optional

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


SECRET_PATTERNS = [
    re.compile(r'\bpassword\w*\s*[=:]\s*["\'][A-Za-z0-9+/=_-]+["\']', re.IGNORECASE),
    re.compile(r'\bsecret\w*\s*[=:]\s*["\'][A-Za-z0-9+/=_-]+["\']', re.IGNORECASE),
    re.compile(r'\bapi[_-]?key\w*\s*[=:]\s*["\'][A-Za-z0-9+/=_-]+["\']', re.IGNORECASE),
    re.compile(r'\btoken\w*\s*[=:]\s*["\'][A-Za-z0-9+/=_-]+["\']', re.IGNORECASE),
]


class HardcodedSecretsRule(BaseRule):
    """Check for hardcoded secrets/passwords/API keys in code."""

    @property
    def name(self) -> str:
        return "Java-HardcodedSecrets"

    @property
    def description(self) -> str:
        return "Detects hardcoded secrets, passwords, and API keys that should not be in source code"


    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        return self._check_line(file_diff.file_path, change.line_number, change.content)

    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        findings = []
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            findings.extend(self._check_line(file_path, i, line))
        return findings

    def _check_line(self, file_path: str, line_number: int, content: str) -> List[RuleFinding]:
        findings = []
        # Remove comments to avoid matching in them
        content_without_comments = self._remove_comments(content)
        for pattern in SECRET_PATTERNS:
            match = pattern.search(content_without_comments)
            if match:
                # Check if the match is not inside a string literal
                if not self._is_pattern_in_string(content_without_comments, match.start(), match.end()):
                    findings.append(RuleFinding(
                        file_path=file_path,
                        line_number=line_number,
                        rule_name=self.name,
                        message="Found potential hardcoded secret/password/api key. Secrets should be in configuration, not in source code.",
                        severity="BLOCK",
                        code_snippet=content.strip()
                    ))
        return findings
