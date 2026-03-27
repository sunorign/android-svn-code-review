import re
from typing import List, Tuple, Optional

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


DEBUG_LOG_PATTERNS = [
    (re.compile(r'System\.out\.println'), 'System.out.println'),
    (re.compile(r'System\.err\.println'), 'System.err.println'),
    (re.compile(r'Log\.d\b'), 'Log.d'),
    (re.compile(r'Log\.v\b'), 'Log.v'),
]


class DebugLoggingRule(BaseRule):
    """Check for debug logging statements that shouldn't be committed."""

    @property
    def name(self) -> str:
        return "Java-DebugLogging"

    @property
    def description(self) -> str:
        return "Detects debug logging statements (System.out.println, Log.d) that should be removed before commit"


    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        content = change.content.strip()
        line_full = change.content

        if self._is_line_comment(content):
            return findings

        for pattern, display_str in DEBUG_LOG_PATTERNS:
            match = pattern.search(line_full)
            if match:
                if self._is_pattern_in_string(line_full, match.start(), match.end()):
                    continue

                findings.append(RuleFinding(
                    file_path=file_diff.file_path,
                    line_number=change.line_number,
                    rule_name=self.name,
                    message=f"Found debug logging statement `{display_str}` - should be removed before commit",
                    severity="BLOCK",
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

            for pattern, display_str in DEBUG_LOG_PATTERNS:
                match = pattern.search(current_line)
                if match:
                    if self._is_pattern_in_string(current_line, match.start(), match.end()):
                        continue

                    findings.append(RuleFinding(
                        file_path=file_path,
                        line_number=i,
                        rule_name=self.name,
                        message=f"Found debug logging statement `{display_str}` - should be removed before commit",
                        severity="BLOCK",
                        code_snippet=line_stripped
                    ))

        return findings
