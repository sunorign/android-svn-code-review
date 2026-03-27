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
    """Determine if a file should be checked based on path rules."""

    def __init__(self, ignore_patterns: List[str] = None):
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS

    def should_check_file(self, file_path: str) -> ScanResult:
        """Check if this file should be reviewed."""

        # Check for libs changes first
        for pattern in LIBS_PATTERNS:
            if self._match_pattern(file_path, pattern):
                return ScanResult(
                    should_ignore=True,
                    is_libs_change=True,
                    reason="File in libs/ directory - will not review, requires commit message note"
                )

        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if self._match_pattern(file_path, pattern):
                return ScanResult(
                    should_ignore=True,
                    is_libs_change=False,
                    reason=f"Matched ignore pattern: {pattern}"
                )

        # Check file extension
        ext = self._get_extension(file_path)
        if ext not in ALLOWED_EXTENSIONS:
            return ScanResult(
                should_ignore=True,
                is_libs_change=False,
                reason=f"File type {ext} not supported for review"
            )

        return ScanResult(
            should_ignore=False,
            is_libs_change=False
        )

    def should_check_extension(self, file_path: str) -> bool:
        """Check if file extension is supported for code review."""
        ext = self._get_extension(file_path)
        return ext in ALLOWED_EXTENSIONS

    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """Simple pattern matching - supports trailing slash for directories."""
        # Convert unix-style path to match any separator
        path = file_path.replace('\\', '/')

        if pattern.endswith('/'):
            # Directory pattern: match any file under this directory
            return f"/{pattern}".strip('/') in f"/{path}".strip('/') or path.startswith(pattern.strip('/'))
        return pattern in path

    def scan(self, file_diffs: List) -> dict:
        """Scan and filter file diffs, collect libs notifications."""
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
        """Get lowercase file extension including dot."""
        parts = file_path.split('.')
        if len(parts) > 1:
            return f'.{parts[-1].lower()}'
        return ''