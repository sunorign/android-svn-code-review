from typing import List

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


# 禁止提交的二进制文件扩展名
BINARY_EXTENSIONS = ['.apk', '.dex', '.jar']


class BinaryFilesRule(BaseRule):
    """检查不应提交的禁止性二进制文件。

    APK、DEX、JAR等二进制文件应通过包管理器进行管理。
    """

    @property
    def name(self) -> str:
        return "Android-BinaryFiles"

    @property
    def description(self) -> str:
        return "检测不应提交的禁止性二进制文件（APK、DEX、JAR）"

    def _is_binary_file(self, file_path: str, content: str) -> bool:
        """基于扩展名或内容检查文件是否为二进制文件。"""
        # 检查文件扩展名
        for ext in BINARY_EXTENSIONS:
            if file_path.lower().endswith(ext):
                return True

        # 检查不可打印字符比例（超过10%认为是二进制文件）
        non_printable_count = 0
        total_count = len(content)

        if total_count == 0:
            return False

        for char in content:
            # 可打印字符包括：空格、ASCII 32-126，以及换行、回车、制表符
            if char not in ' \t\n\r' and (ord(char) < 32 or ord(char) > 126):
                non_printable_count += 1

        non_printable_ratio = non_printable_count / total_count
        if non_printable_ratio > 0.1:  # 超过10%不可打印字符
            return True

        # 检查文件内容是否包含空字节（保留作为额外检查）
        if '\x00' in content:
            return True

        return False

    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        content = change.content.strip()

        # 避免误报：跳过注释和字符串中的内容
        if self._is_line_comment(content):
            return findings

        # 如果文件是禁止的二进制文件类型，直接标记
        if self._is_binary_file(file_diff.file_path, change.content):
            findings.append(RuleFinding(
                file_path=file_diff.file_path,
                line_number=change.line_number,
                rule_name=self.name,
                message=f"二进制文件 `{file_diff.file_path}` 不应提交 - 请使用包管理器代替",
                severity="BLOCK",
                code_snippet=change.content.strip()
            ))

        return findings

    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        findings = []

        if self._is_binary_file(file_path, content):
            findings.append(RuleFinding(
                file_path=file_path,
                line_number=1,
                rule_name=self.name,
                message=f"二进制文件 `{file_path}` 不应提交 - 请使用包管理器代替",
                severity="BLOCK",
                code_snippet="二进制文件内容未显示"
            ))

        return findings
