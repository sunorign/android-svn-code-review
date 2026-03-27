import re
from typing import List, Tuple, Optional

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


class MemoryLeakRule(BaseRule):
    """检查非静态内部类持有 Activity 引用可能导致的内存泄漏风险。"""

    # 可能导致内存泄漏的非静态内部类模式
    INNER_CLASS_PATTERNS = [
        (re.compile(r'private\s+class\s+[a-zA-Z_][a-zA-Z0-9_]*\s+implements\s+View\.OnClickListener'),
         '非静态内部 OnClickListener 类'),
        (re.compile(r'private\s+class\s+[a-zA-Z_][a-zA-Z0-9_]*\s+implements\s+Runnable'),
         '非静态内部 Runnable 类'),
        (re.compile(r'private\s+class\s+[a-zA-Z_][a-zA-Z0-9_]*\s+implements\s+View\.OnTouchListener'),
         '非静态内部 OnTouchListener 类'),
        (re.compile(r'private\s+class\s+[a-zA-Z_][a-zA-Z0-9_]*\s+implements\s+View\.OnLongClickListener'),
         '非静态内部 OnLongClickListener 类'),
        (re.compile(r'private\s+class\s+[a-zA-Z_][a-zA-Z0-9_]*\s+extends\s+AsyncTask'),
         '非静态内部 AsyncTask 类'),
    ]

    @property
    def name(self) -> str:
        return "Java-MemoryLeak"

    @property
    def description(self) -> str:
        return "检测非静态内部类持有 Activity 引用可能导致的内存泄漏"

    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        content = change.content.strip()
        line_full = change.content

        if self._is_line_comment(content):
            return findings

        for pattern, class_type in self.INNER_CLASS_PATTERNS:
            match = pattern.search(line_full)
            if match:
                if self._is_pattern_in_string(line_full, match.start(), match.end()):
                    continue

                findings.append(RuleFinding(
                    file_path=file_diff.file_path,
                    line_number=change.line_number,
                    rule_name=self.name,
                    message=f"发现潜在内存泄漏: {class_type} 持有 Activity 引用",
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

            for pattern, class_type in self.INNER_CLASS_PATTERNS:
                match = pattern.search(current_line)
                if match:
                    if self._is_pattern_in_string(current_line, match.start(), match.end()):
                        continue

                    findings.append(RuleFinding(
                        file_path=file_path,
                        line_number=i,
                        rule_name=self.name,
                        message=f"发现潜在内存泄漏: {class_type} 持有 Activity 引用",
                        severity="WARNING",
                        code_snippet=line_stripped
                    ))

        return findings