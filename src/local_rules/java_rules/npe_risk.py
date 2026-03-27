import re
from typing import List, Tuple, Optional

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


class NPERiskRule(BaseRule):
    """Check for potential NPE risks where null values might be accessed."""

    # Patterns for method calls on potentially null variables
    NPE_PATTERNS = [
        # Common method calls that could cause NPE
        (re.compile(r'\.toString\(\)'), '.toString()'),
        (re.compile(r'\.equals\('), '.equals('),
        (re.compile(r'\.charAt\('), '.charAt('),
        (re.compile(r'\.length\(\)'), '.length()'),
        (re.compile(r'\.trim\(\)'), '.trim()'),
        (re.compile(r'\.isEmpty\(\)'), '.isEmpty()'),
        # Check for if (!var) but var could be null
        (re.compile(r'if\s*\(\s*!\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\)'), 'boolean check on potentially null'),
        # Check for var == null or var != null patterns but then not used properly
        (re.compile(r'==\s*null'), 'null comparison'),
        (re.compile(r'!=\s*null'), 'non-null comparison'),
    ]

    # Simple pattern to detect variable usage after possible null check
    NULL_CHECK_PATTERNS = [
        re.compile(r'if\s*\(\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*==\s*null\s*\)'),
        re.compile(r'if\s*\(\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*!=\s*null\s*\)'),
    ]

    @property
    def name(self) -> str:
        return "Java-NPERisk"

    @property
    def description(self) -> str:
        return "Detects potential NPE risks where methods are called on potentially null variables"


    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        content = change.content.strip()
        line_full = change.content

        if self._is_line_comment(content):
            return findings

        # Check for direct method calls on objects
        for pattern, display_str in self.NPE_PATTERNS:
            match = pattern.search(line_full)
            if match:
                if self._is_pattern_in_string(line_full, match.start(), match.end()):
                    continue

                # Skip if this looks like it's in a null check context
                if '== null' in line_full or '!= null' in line_full:
                    continue

                findings.append(RuleFinding(
                    file_path=file_diff.file_path,
                    line_number=change.line_number,
                    rule_name=self.name,
                    message=f"Found potential NPE risk: calling `{display_str}` on potentially null variable",
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

            # Check for direct method calls on objects
            for pattern, display_str in self.NPE_PATTERNS:
                match = pattern.search(current_line)
                if match:
                    if self._is_pattern_in_string(current_line, match.start(), match.end()):
                        continue

                    # Skip if this looks like it's in a null check context
                    if '== null' in current_line or '!= null' in current_line:
                        continue

                    findings.append(RuleFinding(
                        file_path=file_path,
                        line_number=i,
                        rule_name=self.name,
                        message=f"Found potential NPE risk: calling `{display_str}` on potentially null variable",
                        severity="WARNING",
                        code_snippet=line_stripped
                    ))

        return findings