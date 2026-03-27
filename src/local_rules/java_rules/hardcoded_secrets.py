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
    """检查代码中硬编码的密钥/密码/API密钥。"""

    @property
    def name(self) -> str:
        return "Java-HardcodedSecrets"

    @property
    def description(self) -> str:
        return "检测硬编码的密钥、密码和API密钥，这些内容不应出现在源代码中"


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
        # 移除注释以避免在注释中匹配到内容
        content_without_comments = self._remove_comments(content)
        for pattern in SECRET_PATTERNS:
            match = pattern.search(content_without_comments)
            if match:
                # 检查匹配结果是否不在字符串字面量中
                if not self._is_pattern_in_string(content_without_comments, match.start(), match.end()):
                    findings.append(RuleFinding(
                        file_path=file_path,
                        line_number=line_number,
                        rule_name=self.name,
                        message="发现潜在的硬编码密钥/密码/API密钥。密钥应放在配置文件中，而不是源代码里。",
                        severity="BLOCK",
                        code_snippet=content.strip()
                    ))
        return findings
