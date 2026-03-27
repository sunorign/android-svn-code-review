from dataclasses import dataclass
from typing import List, Tuple


DEFAULT_IGNORE_PATTERNS = [
    'build/',
    '*/build/',
    'app/build/',
    'generated/',
    '*/generated/',
    '.git/',
    '.svn/',
]

LIBS_PATTERNS = [
    'libs/',
    '*/libs/',
]

ALLOWED_EXTENSIONS = {
    '.java', '.kotlin', '.kt',
    '.xml', '.gradle',
}


@dataclass
class ScanResult:
    should_ignore: bool
    is_libs_change: bool
    reason: str = ""


class FileScanner:
    """根据路径规则判断是否应检查文件。"""

    def __init__(self, ignore_patterns: List[str] = None):
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS

    def should_check_file(self, file_path: str) -> ScanResult:
        """检查此文件是否应被审查。"""

        # 首先检查libs目录变更
        for pattern in LIBS_PATTERNS:
            if self._match_pattern(file_path, pattern):
                return ScanResult(
                    should_ignore=True,
                    is_libs_change=True,
                    reason="文件在libs/目录中 - 不会进行审查，需要在提交信息中注明"
                )

        # 检查忽略模式
        for pattern in self.ignore_patterns:
            if self._match_pattern(file_path, pattern):
                return ScanResult(
                    should_ignore=True,
                    is_libs_change=False,
                    reason=f"匹配到忽略模式: {pattern}"
                )

        # 检查文件扩展名
        ext = self._get_extension(file_path)
        if ext not in ALLOWED_EXTENSIONS:
            return ScanResult(
                should_ignore=True,
                is_libs_change=False,
                reason=f"文件类型{ext}不支持审查"
            )

        return ScanResult(
            should_ignore=False,
            is_libs_change=False
        )

    def should_check_extension(self, file_path: str) -> bool:
        """检查文件扩展名是否支持代码审查。"""
        ext = self._get_extension(file_path)
        return ext in ALLOWED_EXTENSIONS

    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """简单模式匹配 - 支持目录结尾的斜杠。"""
        # 将Unix风格路径转换为兼容任意分隔符
        path = file_path.replace('\\', '/')

        if pattern.endswith('/'):
            # 目录模式: 匹配此目录下的任何文件
            return f"/{pattern}".strip('/') in f"/{path}".strip('/') or path.startswith(pattern.strip('/'))
        return pattern in path

    def scan(self, file_diffs: List) -> dict:
        """扫描并过滤文件差异，收集libs目录变更通知。"""
        file_diffs_to_check = []
        libs_notifications = []

        from src.local_rules.base_rule import RuleFinding

        for file_diff in file_diffs:
            result = self.should_check_file(file_diff.file_path)

            if result.is_libs_change:
                libs_notifications.append(RuleFinding(
                    file_path=file_diff.file_path,
                    line_number=None,
                    rule_name="LibraryChange",
                    message=result.reason,
                    severity="NOTIFICATION"
                ))
            elif not result.should_ignore:
                file_diffs_to_check.append(file_diff)

        return {
            "file_diffs": file_diffs_to_check,
            "libs_notifications": libs_notifications
        }

    def _get_extension(self, file_path: str) -> str:
        """获取小写的文件扩展名（包含点号）。"""
        parts = file_path.split('.')
        if len(parts) > 1:
            return f'.{parts[-1].lower()}'
        return ''