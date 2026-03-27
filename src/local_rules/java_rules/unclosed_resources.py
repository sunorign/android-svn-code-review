import re
from typing import List, Tuple, Optional

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


class UnclosedResourcesRule(BaseRule):
    """Check for unclosed resources like Cursor, Stream, Connection, FileInputStream etc."""

    RESOURCE_PATTERNS = [
        (re.compile(r'new\s+Cursor\s*\('), 'Cursor'),
        (re.compile(r'new\s+FileInputStream\s*\('), 'FileInputStream'),
        (re.compile(r'new\s+FileOutputStream\s*\('), 'FileOutputStream'),
        (re.compile(r'new\s+Connection\s*\('), 'Connection'),
        (re.compile(r'new\s+Statement\s*\('), 'Statement'),
        (re.compile(r'Stream\s*<'), 'Stream'),
    ]

    @property
    def name(self) -> str:
        return "Java-UnclosedResources"

    @property
    def description(self) -> str:
        return "Detects unclosed resources like Cursor, Stream, Connection, FileInputStream that should be properly closed"


    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        content = change.content.strip()
        line_full = change.content

        if self._is_line_comment(content):
            return findings

        for pattern, resource_type in self.RESOURCE_PATTERNS:
            match = pattern.search(line_full)
            if match:
                if self._is_pattern_in_string(line_full, match.start(), match.end()):
                    continue

                findings.append(RuleFinding(
                    file_path=file_diff.file_path,
                    line_number=change.line_number,
                    rule_name=self.name,
                    message=f"Found unclosed resource `{resource_type}` - should be properly closed",
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

            for pattern, resource_type in self.RESOURCE_PATTERNS:
                match = pattern.search(current_line)
                if match:
                    if self._is_pattern_in_string(current_line, match.start(), match.end()):
                        continue

                    findings.append(RuleFinding(
                        file_path=file_path,
                        line_number=i,
                        rule_name=self.name,
                        message=f"Found unclosed resource `{resource_type}` - should be properly closed",
                        severity="WARNING",
                        code_snippet=line_stripped
                    ))

        return findings