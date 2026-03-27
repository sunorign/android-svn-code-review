import re
from typing import List

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


# 匹配 http:// 或 https:// 后面跟着IP地址或域名，但不是 localhost 的模式
HARDCODED_URL_PATTERN = re.compile(
    r'https?://'  # 匹配 http:// 或 https://
    r'(?!localhost|127\.0\.0\.1)'  # 排除 localhost 和 127.0.0.1
    r'(?:(?:[a-zA-Z0-9-]+\.)+[a-zA-Z0-9]{2,}|'  # 域名模式（支持 .io, .app, .tech 等现代顶级域名）
    r'(?:(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|'  # IPv4地址模式
    r'\[([0-9a-fA-F:.]+)\])'  # IPv6地址模式（带方括号，如 [::1] 或 [2001:db8::1]）
    r'(?::\d+)?'  # 可选的端口号
    r'(?:/[^\s"]*)?'  # 可选的路径
)


class HardcodedUrlsRule(BaseRule):
    """Check for hardcoded URLs/IP addresses in code.

    URLs/IP addresses should be placed in configuration files instead of being hardcoded.
    """

    @property
    def name(self) -> str:
        return "Android-HardcodedUrls"

    @property
    def description(self) -> str:
        return "Detects hardcoded URLs or IP addresses that should be in configuration files"

    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        content = change.content.strip()
        line_full = change.content

        if self._is_line_comment(content):
            return findings

        match = HARDCODED_URL_PATTERN.search(line_full)
        if match:
            if self._is_pattern_in_string(line_full, match.start(), match.end()):
                findings.append(RuleFinding(
                    file_path=file_diff.file_path,
                    line_number=change.line_number,
                    rule_name=self.name,
                    message=f"Found hardcoded URL/IP: `{match.group()}` - should be placed in configuration file",
                    severity="WARNING",
                    code_snippet=content
                ))

        return findings

    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        findings = []
        lines = content.splitlines()
        in_multiline_comment = False

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            current_line = line

            # Handle multi-line comments
            if in_multiline_comment:
                if '*/' in current_line:
                    in_multiline_comment = False
                    current_line = current_line[current_line.index('*/') + 2:]
                else:
                    continue

            if '/*' in current_line:
                if '*/' in current_line and current_line.index('/*') < current_line.index('*/'):
                    continue
                else:
                    in_multiline_comment = True
                    current_line = current_line[:current_line.index('/*')]
                    if not current_line.strip():
                        continue

            if current_line.strip().startswith('//'):
                continue

            match = HARDCODED_URL_PATTERN.search(current_line)
            if match:
                if self._is_pattern_in_string(current_line, match.start(), match.end()):
                    findings.append(RuleFinding(
                        file_path=file_path,
                        line_number=i,
                        rule_name=self.name,
                        message=f"Found hardcoded URL/IP: `{match.group()}` - should be placed in configuration file",
                        severity="WARNING",
                        code_snippet=line_stripped
                    ))

        return findings
