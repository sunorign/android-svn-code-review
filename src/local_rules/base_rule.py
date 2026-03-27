import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from src.diff_parser import DiffChange, FileDiff


@dataclass
class RuleFinding:
    """表示规则发现的问题。"""
    file_path: str
    line_number: int
    rule_name: str
    message: str
    severity: str  # "BLOCK" 或 "WARNING"
    code_snippet: Optional[str] = None

    def is_blocking(self) -> bool:
        return self.severity.upper() == "BLOCK"


class BaseRule(ABC):
    """所有本地审查规则的基类。"""

    @property
    @abstractmethod
    def name(self) -> str:
        """报告中显示的规则名称。"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """规则检查内容的简要描述。"""
        pass

    @abstractmethod
    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        """检查差异中的单个变更行。

        参数:
            file_diff: 整个文件的差异
            change: 要检查的特定变更行

        返回:
            发现的问题列表（无问题则为空）
        """
        pass

    @abstractmethod
    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        """检查整个文件内容（用于全面审查模式）。

        参数:
            file_path: 文件路径
            content: 文件的完整内容

        返回:
            发现的问题列表（无问题则为空）
        """
        pass

    def _is_pattern_in_string(self, line: str, match_start: int, match_end: int) -> bool:
        """检查匹配到的模式是否在字符串字面量内部。"""
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
        """检查该行是否是单行注释。"""
        stripped = line.strip()
        return stripped.startswith('//') or stripped.startswith('/*')

    def _remove_comments(self, content: str) -> str:
        """从内容中移除注释以避免在注释中匹配。"""
        # 处理 /* ... */ 注释（包括行尾未关闭的）
        if '/*' in content:
            start_idx = content.find('/*')
            end_idx = content.find('*/', start_idx)
            if end_idx != -1:
                # 移除已关闭的注释块
                content = content[:start_idx] + content[end_idx + 2:]
            else:
                # 移除从 /* 到行尾的所有内容
                content = content[:start_idx]

        # 移除 // 注释
        content = re.sub(r'//.*$', '', content)
        return content