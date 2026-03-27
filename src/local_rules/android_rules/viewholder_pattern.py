import re
from typing import List

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


# 检查是否在 getView() 或 onBindViewHolder() 方法中 - 支持完整方法签名
METHOD_PATTERNS = [
    re.compile(r'(?:public|protected|private|static|final|abstract|synchronized|native|transient|volatile)?'
               r'\s*[^\s()]+\s*getView\('),
    re.compile(r'(?:public|protected|private|static|final|abstract|synchronized|native|transient|volatile)?'
               r'\s*[^\s()]+\s*onBindViewHolder\(')
]

# 匹配 findViewById 调用
FIND_VIEW_BY_ID_PATTERN = re.compile(r'findViewById')

# 匹配 ViewHolder 内部类定义
# 匹配类似 "class ViewHolder" 或 "class MyViewHolder" 的内部类，而不是包含 ViewHolder 作为泛型参数的类
VIEW_HOLDER_PATTERN = re.compile(r'class\s+(\w+ViewHolder|ViewHolder)\s*\{')


class ViewHolderPatternRule(BaseRule):
    """检查 Android 代码中 ViewHolder 模式的不当使用。

    如果在 getView() 或 onBindViewHolder() 中多次调用 findViewById，
    表明 ViewHolder 模式使用不正确。
    """

    @property
    def name(self) -> str:
        return "Android-ViewHolderPattern"

    @property
    def description(self) -> str:
        return "检测 getView() 或 onBindViewHolder() 中 ViewHolder 模式的不当使用"

    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        content = change.content.strip()
        line_full = change.content

        if self._is_line_comment(content):
            return findings

        # 检查是否包含 findViewById 调用
        if FIND_VIEW_BY_ID_PATTERN.search(line_full):
            # 如果包含 findViewById，检查是否在目标方法中
            # 由于 diff 只包含单行变更，我们需要基于文件名或上下文线索判断
            # 这里采用简单的启发式方法：如果是 Adapter 类或包含目标方法名的文件
            if 'Adapter' in file_diff.file_path or any(pattern.search(line_full) for pattern in METHOD_PATTERNS):
                # 简单检查是否在 ViewHolder 内部类中（通过查看当前行或上下文是否包含 ViewHolder 类定义）
                if not VIEW_HOLDER_PATTERN.search(line_full) and 'ViewHolder' not in line_full:
                    findings.append(RuleFinding(
                        file_path=file_diff.file_path,
                        line_number=change.line_number,
                        rule_name=self.name,
                        message="检测到 findViewById 调用 - 应使用 ViewHolder 模式以提高性能",
                        severity="WARNING",
                        code_snippet=content
                    ))

        return findings

    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        findings = []
        lines = content.splitlines()
        in_target_method = False
        in_view_holder = False
        brace_count = 0

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            current_line = line

            # 检查 ViewHolder 内部类进入
            if VIEW_HOLDER_PATTERN.search(line_stripped) and not line_stripped.startswith('//') and not self._is_line_comment(line_stripped):
                in_view_holder = True

            # 检查目标方法进入
            for pattern in METHOD_PATTERNS:
                if pattern.search(line_stripped) and not line_stripped.startswith('//') and not self._is_line_comment(line_stripped):
                    in_target_method = True

            # 跟踪大括号计数
            for char in current_line:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    if brace_count > 0:
                        brace_count -= 1
                        # 简单的方法退出检测：当大括号计数减少时，检查是否应该退出方法或类
                        if in_view_holder and brace_count == 0:
                            in_view_holder = False
                        if in_target_method and brace_count == 0:
                            in_target_method = False

            # 检查是否在目标方法内且包含 findViewById 调用，但不在 ViewHolder 内部类中
            if in_target_method and FIND_VIEW_BY_ID_PATTERN.search(current_line) and not self._is_line_comment(line_stripped) and not in_view_holder:
                findings.append(RuleFinding(
                    file_path=file_path,
                    line_number=i,
                    rule_name=self.name,
                    message="在 getView()/onBindViewHolder() 中调用 findViewById - 应使用 ViewHolder 模式",
                    severity="WARNING",
                    code_snippet=line_stripped
                ))

        return findings
