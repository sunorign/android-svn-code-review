import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DiffChange:
    """表示diff中的单个行变更。"""
    line_number: int  # 工作副本中的新行号
    content: str
    is_added: bool
    is_removed: bool


@dataclass
class FileDiff:
    """单个文件的全部变更。"""
    file_path: str
    is_new_file: bool
    is_deleted: bool
    changes: List[DiffChange] = field(default_factory=list)

    @property
    def added_lines(self) -> List[DiffChange]:
        return [c for c in self.changes if c.is_added]


class DiffParser:
    """将SVN diff输出解析为结构化数据。"""

    # SVN diff的正则表达式模式
    INDEX_PATTERN = re.compile(r'^Index: (.+)$')
    HEADER_OLD_PATTERN = re.compile(r'^--- (.+)\s+(\(.+\))\s*$')
    HEADER_NEW_PATTERN = re.compile(r'^\+\+\+ (.+)\s+(\(.+\))\s*$')
    HUNK_PATTERN = re.compile(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@.*$')

    def __init__(self, diff_text: str):
        self.lines = diff_text.splitlines()
        self.current_line = 0

    def parse(self) -> List[FileDiff]:
        """解析整个diff并返回FileDiff对象列表。"""
        file_diffs = []
        current_file_diff: Optional[FileDiff] = None
        current_new_line = 0

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line].rstrip('\n')
            self.current_line += 1

            # 跳过分隔线
            if line.startswith('==='):
                continue

            # 检查新文件索引
            index_match = self.INDEX_PATTERN.match(line)
            if index_match:
                if current_file_diff is not None and current_file_diff.changes:
                    file_diffs.append(current_file_diff)
                file_path = index_match.group(1)
                current_file_diff = FileDiff(
                    file_path=file_path,
                    is_new_file=False,
                    is_deleted=False
                )
                continue

            # 检查新旧文件头以检测新增/删除的文件
            old_match = self.HEADER_OLD_PATTERN.match(line)
            if old_match and current_file_diff is not None:
                old_label = old_match.group(2)
                if old_label == '(revision 0)' or old_label == '(nonexistent)':
                    current_file_diff.is_new_file = True
                # 跳过旧文件头行
                continue

            new_match = self.HEADER_NEW_PATTERN.match(line)
            if new_match and current_file_diff is not None:
                new_label = new_match.group(2)
                if new_label == '(revision 0)' or new_label == '(nonexistent)':
                    current_file_diff.is_deleted = True
                # 跳过新文件头行
                continue

            # 检查hunk起始
            hunk_match = self.HUNK_PATTERN.match(line)
            if hunk_match and current_file_diff is not None:
                current_new_line = int(hunk_match.group(2))
                continue

            # 处理变更行
            if current_file_diff is not None and line.startswith(('+', '-', ' ')):
                if line.startswith('+'):
                    current_file_diff.changes.append(DiffChange(
                        line_number=current_new_line,
                        content=line[1:],
                        is_added=True,
                        is_removed=False
                    ))
                    current_new_line += 1
                elif line.startswith(' '):
                    current_new_line += 1
                # 删除的行不计入新行号
                continue

        # 添加最后一个文件
        if current_file_diff is not None and (current_file_diff.changes or current_file_diff.is_new_file):
            file_diffs.append(current_file_diff)

        return file_diffs
