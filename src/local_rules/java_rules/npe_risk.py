import re
from typing import List, Tuple, Optional

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


class NPERiskRule(BaseRule):
    """检查可能访问空值的潜在NPE风险。"""

    # 可能为空的变量上的方法调用模式
    NPE_PATTERNS = [
        # 可能导致NPE的常见方法调用
        (re.compile(r'\.toString\(\)'), '.toString()'),
        (re.compile(r'\.equals\('), '.equals('),
        (re.compile(r'\.charAt\('), '.charAt('),
        (re.compile(r'\.length\(\)'), '.length()'),
        (re.compile(r'\.trim\(\)'), '.trim()'),
        (re.compile(r'\.isEmpty\(\)'), '.isEmpty()'),
        # 检查 if (!var) 但 var 可能为 null 的情况
        (re.compile(r'if\s*\(\s*!\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\)'), '对可能为空的变量进行布尔检查'),
        # 检查 var == null 或 var != null 模式但未正确使用的情况
        (re.compile(r'==\s*null'), '空值比较'),
        (re.compile(r'!=\s*null'), '非空值比较'),
    ]

    # 用于检测空值检查后变量使用的简单模式
    NULL_CHECK_PATTERNS = [
        re.compile(r'if\s*\(\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*==\s*null\s*\)'),
        re.compile(r'if\s*\(\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*!=\s*null\s*\)'),
    ]

    @property
    def name(self) -> str:
        return "Java-NPERisk"

    @property
    def description(self) -> str:
        return "检测在可能为空的变量上调用方法的潜在NPE风险"


    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        content = change.content.strip()
        line_full = change.content

        if self._is_line_comment(content):
            return findings

        # 检查对对象的直接方法调用
        for pattern, display_str in self.NPE_PATTERNS:
            match = pattern.search(line_full)
            if match:
                if self._is_pattern_in_string(line_full, match.start(), match.end()):
                    continue

                # 如果看起来是在空值检查上下文中，则跳过
                if '== null' in line_full or '!= null' in line_full:
                    continue

                findings.append(RuleFinding(
                    file_path=file_diff.file_path,
                    line_number=change.line_number,
                    rule_name=self.name,
                    message=f"发现潜在NPE风险：在可能为空的变量上调用 `{display_str}`",
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

            # 检查对对象的直接方法调用
            for pattern, display_str in self.NPE_PATTERNS:
                match = pattern.search(current_line)
                if match:
                    if self._is_pattern_in_string(current_line, match.start(), match.end()):
                        continue

                    # 如果看起来是在空值检查上下文中，则跳过
                    if '== null' in current_line or '!= null' in current_line:
                        continue

                    findings.append(RuleFinding(
                        file_path=file_path,
                        line_number=i,
                        rule_name=self.name,
                        message=f"发现潜在NPE风险：在可能为空的变量上调用 `{display_str}`",
                        severity="WARNING",
                        code_snippet=line_stripped
                    ))

        return findings