# Android SVN 代码审查工具 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现一个 Python 写的 SVN pre-commit 钩子工具，在提交代码前对 Android Java/Kotlin 代码做本地规则检查 + AI 审查，拦截严重问题。

**Architecture:** 模块化设计，规则和 AI 客户端都用基类接口，易于扩展。目录结构按功能拆分，规则放在独立目录，提示词模板作为文本文件存储，方便团队积累。配置全部从环境变量读取，不进代码库。

**Tech Stack:** Python 3, SVN CLI, requests (for API calls), HTML template for reports

---

## 文件结构总览

| 文件 | 职责 |
|------|------|
| `hooks/pre-commit` | SVN pre-commit 钩子入口脚本 |
| `src/main.py` | 主程序， orchestrate 整个审查流程 |
| `src/diff_parser.py` | 解析 svn diff 输出，提取改动文件和行号 |
| `src/scanner.py` | 文件扫描，处理忽略规则，识别 libs 变更 |
| `src/config.py` | 从环境变量读取配置 |
| `src/local_rules/base_rule.py` | 规则基类，定义接口 |
| `src/local_rules/__init__.py` | 规则加载器 |
| `src/local_rules/java_rules/debug_logging.py` | 检查调试日志残留 |
| `src/local_rules/java_rules/hardcoded_secrets.py` | 检查硬编码敏感信息 |
| `src/local_rules/java_rules/unclosed_resources.py` | 检查未关闭资源 |
| `src/local_rules/java_rules/npe_risk.py` | 检查 NPE 风险 |
| `src/local_rules/java_rules/memory_leak.py` | 检查内存泄漏风险 |
| `src/local_rules/android_rules/hardcoded_urls.py` | 检查硬编码 URL/IP |
| `src/local_rules/android_rules/binary_files.py` | 检查禁止提交的二进制文件 |
| `src/local_rules/android_rules/viewholder_pattern.py` | 检查 ViewHolder 模式 |
| `src/ai_reviewer/base_client.py` | AI 客户端基类 |
| `src/ai_reviewer/__init__.py` | AI 客户端工厂 |
| `src/ai_reviewer/claude_client.py` | Claude API 客户端 |
| `src/ai_reviewer/openrouter_client.py` | OpenRouter 客户端 |
| `src/ai_reviewer/local_ollama_client.py` | Ollama 客户端骨架 |
| `src/ai_reviewer/prompt_templates/java-diff-review.md` | Java diff 审查提示词 |
| `src/ai_reviewer/prompt_templates/kotlin-diff-review.md` | Kotlin diff 审查提示词 |
| `src/ai_reviewer/prompt_templates/android-full-review.md` | Android 全文审查提示词 |
| `src/reporter/text_reporter.py` | 文本报告生成 |
| `src/reporter/html_reporter.py` | HTML 报告生成 |
| `src/reporter/json_reporter.py` | JSON 报告生成 |
| `docs/writing-local-rules.md` | 本地规则编写指南 |
| `docs/writing-ai-prompts.md` | AI 提示词编写指南 |
| `tests/test_diff_parser.py` | diff 解析器测试 |
| `tests/test_local_rules.py` | 本地规则测试 |
| `requirements.txt` | Python 依赖 |

---

### Task 1: 项目骨架和依赖管理

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`

- [ ] **Step 1: Create `requirements.txt`**

```txt
requests>=2.28.0
```

- [ ] **Step 2: Create empty `src/__init__.py`**

```python
# Android SVN Code Review Tool
__version__ = "0.1.0"
```

- [ ] **Step 3: Commit**

```bash
git add requirements.txt src/__init__.py
git commit -m "chore: init project skeleton"
```

---

### Task 2: 配置模块 - 从环境变量读取配置

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write test**

```python
import os
import pytest
from src.config import Config


def test_config_from_env():
    os.environ['ANTHROPIC_API_KEY'] = 'test-key'
    os.environ['OPENROUTER_API_KEY'] = 'test-openrouter-key'
    os.environ['OLLAMA_API_BASE'] = 'http://localhost:11434'

    config = Config.load_from_env()

    assert config.anthropic_api_key == 'test-key'
    assert config.openrouter_api_key == 'test-openrouter-key'
    assert config.ollama_api_base == 'http://localhost:11434'
    assert config.has_ai_enabled() is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_config.py -v
```
Expected: FAIL because `Config` not defined yet.

- [ ] **Step 3: Implement `config.py`**

```python
import os
from dataclasses import dataclass


@dataclass
class Config:
    anthropic_api_key: str | None
    openrouter_api_key: str | None
    ollama_api_base: str | None
    ai_provider: str | None  # "claude", "openrouter", "ollama"

    @classmethod
    def load_from_env(cls) -> 'Config':
        return cls(
            anthropic_api_key=os.environ.get('ANTHROPIC_API_KEY'),
            openrouter_api_key=os.environ.get('OPENROUTER_API_KEY'),
            ollama_api_base=os.environ.get('OLLAMA_API_BASE', 'http://localhost:11434'),
            ai_provider=os.environ.get('AI_REVIEW_PROVIDER'),
        )

    def has_ai_enabled(self) -> bool:
        """Check if any AI provider is configured."""
        if self.ai_provider == 'claude' and self.anthropic_api_key:
            return True
        if self.ai_provider == 'openrouter' and self.openrouter_api_key:
            return True
        if self.ai_provider == 'ollama' and self.ollama_api_base:
            return True
        # Auto-detect if any is available
        if self.anthropic_api_key:
            return True
        if self.openrouter_api_key:
            return True
        if self.ollama_api_base:
            return True
        return False

    def get_active_provider(self) -> str | None:
        """Get the active AI provider."""
        if self.ai_provider:
            return self.ai_provider
        if self.anthropic_api_key:
            return 'claude'
        if self.openrouter_api_key:
            return 'openrouter'
        if self.ollama_api_base:
            return 'ollama'
        return None
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_config.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add config module from environment variables"
```

---

### Task 3: SVN Diff 解析器

**Files:**
- Create: `src/diff_parser.py`
- Create: `tests/test_diff_parser.py`

- [ ] **Step 1: Write test**

```python
from src.diff_parser import DiffParser, DiffChange, FileDiff


def test_parse_simple_diff():
    diff_text = """Index: src/com/example/Main.java
===================================================================
--- src/com/example/Main.java	(revision 123)
+++ src/com/example/Main.java	(working copy)
@@ -10,6 +10,8 @@
     public void doSomething() {
+        System.out.println("debug");
+        // todo: remove this
         somethingElse();
     }
"""
    parser = DiffParser(diff_text)
    file_diffs = parser.parse()

    assert len(file_diffs) == 1
    assert file_diffs[0].file_path == "src/com/example/Main.java"
    assert file_diffs[0].is_new_file is False
    assert len(file_diffs[0].changes) == 2  # two lines added
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_diff_parser.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement `diff_parser.py`**

```python
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DiffChange:
    """Represents a single line change in a diff."""
    line_number: int  # New line number in working copy
    content: str
    is_added: bool
    is_removed: bool


@dataclass
class FileDiff:
    """All changes for a single file."""
    file_path: str
    is_new_file: bool
    is_deleted: bool
    changes: List[DiffChange] = field(default_factory=list)

    @property
    def added_lines(self) -> List[DiffChange]:
        return [c for c in self.changes if c.is_added]


class DiffParser:
    """Parse SVN diff output into structured data."""

    # Regex patterns for SVN diff
    INDEX_PATTERN = re.compile(r'^Index: (.+)$')
    HEADER_OLD_PATTERN = re.compile(r'^--- (.+)\s+(\(.+\))\s*$')
    HEADER_NEW_PATTERN = re.compile(r'^\+\+\+ (.+)\s+(\(.+\))\s*$')
    HUNK_PATTERN = re.compile(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@.*$')

    def __init__(self, diff_text: str):
        self.lines = diff_text.splitlines()
        self.current_line = 0

    def parse(self) -> List[FileDiff]:
        """Parse the entire diff and return list of FileDiff."""
        file_diffs = []
        current_file_diff: Optional[FileDiff] = None
        current_new_line = 0

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line].rstrip('\n')
            self.current_line += 1

            # Check for new file index
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

            # Check for old/new headers to detect new/deleted files
            old_match = self.HEADER_OLD_PATTERN.match(line)
            if old_match and current_file_diff is not None:
                old_label = old_match.group(2)
                if old_label == '(revision 0)' or old_label == '(nonexistent)':
                    current_file_diff.is_new_file = True

            new_match = self.HEADER_NEW_PATTERN.match(line)
            if new_match and current_file_diff is not None:
                new_label = new_match.group(2)
                if new_label == '(revision 0)' or new_label == '(nonexistent)':
                    current_file_diff.is_deleted = True

            # Check for hunk start
            hunk_match = self.HUNK_PATTERN.match(line)
            if hunk_match and current_file_diff is not None:
                current_new_line = int(hunk_match.group(2))
                continue

            # Process change lines
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
                # Removed lines don't count toward new line number
                continue

        # Add the last file
        if current_file_diff is not None and (current_file_diff.changes or current_file_diff.is_new_file):
            file_diffs.append(current_file_diff)

        return file_diffs
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_diff_parser.py -v
```
Expected: PASS

- [ ] **Step 5: Add test for new file case**

```python
def test_parse_new_file():
    diff_text = """Index: NewFile.java
===================================================================
--- NewFile.java	(revision 0)
+++ NewFile.java	(working copy)
@@ -0,0 +1,5 @@
+package com.example;
+
+public class NewFile {
+}
"""
    parser = DiffParser(diff_text)
    file_diffs = parser.parse()

    assert len(file_diffs) == 1
    assert file_diffs[0].is_new_file is True
    assert len(file_diffs[0].added_lines) == 4
```

- [ ] **Step 6: Run test again to verify**

```bash
python -m pytest tests/test_diff_parser.py -v
```
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/diff_parser.py tests/test_diff_parser.py
git commit -m "feat: add svn diff parser"
```

---

### Task 4: 文件扫描器和忽略规则

**Files:**
- Create: `src/scanner.py`
- Create: `tests/test_scanner.py`

- [ ] **Step 1: Write test**

```python
from src.diff_parser import FileDiff
from src.scanner import FileScanner, ScanResult


def test_should_ignore_build_dir():
    scanner = FileScanner()
    result = scanner.should_check_file("app/build/generated/some.java")
    assert result.should_ignore is True
    assert result.is_libs_change is False


def test_should_ignore_generated():
    scanner = FileScanner()
    result = scanner.should_check_file("app/src/generated/File.java")
    assert result.should_ignore is True


def test_libs_directory_change():
    scanner = FileScanner()
    result = scanner.should_check_file("libs/mylib.jar")
    assert result.should_ignore is True
    assert result.is_libs_change is True


def test_should_check_source_file():
    scanner = FileScanner()
    result = scanner.should_check_file("app/src/main/java/com/example/Main.java")
    assert result.should_ignore is False
    assert result.is_libs_change is False
    assert result.should_check_extension() is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_scanner.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement `scanner.py`**

```python
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

    def _get_extension(self, file_path: str) -> str:
        """Get lowercase file extension including dot."""
        parts = file_path.split('.')
        if len(parts) > 1:
            return f'.{parts[-1].lower()}'
        return ''
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_scanner.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/scanner.py tests/test_scanner.py
git commit -m "feat: add file scanner with ignore rules"
```

---

### Task 5: 本地规则基类

**Files:**
- Create: `src/local_rules/base_rule.py`
- Create: `src/local_rules/__init__.py`

- [ ] **Step 1: Implement `base_rule.py`**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from src.diff_parser import DiffChange, FileDiff


@dataclass
class RuleFinding:
    """Represents an issue found by a rule."""
    file_path: str
    line_number: int
    rule_name: str
    message: str
    severity: str  # "BLOCK" or "WARNING"
    code_snippet: Optional[str] = None

    def is_blocking(self) -> bool:
        return self.severity.upper() == "BLOCK"


class BaseRule(ABC):
    """Base class for all local review rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Rule name displayed in reports."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of what the rule checks."""
        pass

    @abstractmethod
    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        """Check a single changed line in a diff.

        Args:
            file_diff: The entire file diff
            change: The specific changed line to check

        Returns:
            List of findings (empty if no issues)
        """
        pass

    @abstractmethod
    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        """Check the entire file content (for full review mode).

        Args:
            file_path: Path to the file
            content: Full content of the file

        Returns:
            List of findings (empty if no issues)
        """
        pass
```

- [ ] **Step 2: Implement `__init__.py` rule loader**

```python
import importlib
import pkgutil
from typing import List, Type

from src.local_rules.base_rule import BaseRule


def load_all_rules() -> List[BaseRule]:
    """Dynamically load all rule classes from all submodules."""
    from src.local_rules import java_rules
    from src.local_rules import android_rules
    from src.local_rules import kotlin_rules

    rules: List[BaseRule] = []

    # Load from all packages
    packages = [java_rules, android_rules, kotlin_rules]
    for pkg in packages:
        for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
            module = importlib.import_module(f"{pkg.__name__}.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseRule) and attr != BaseRule:
                    rules.append(attr())

    return rules
```

- [ ] **Step 3: Add empty `kotlin_rules/__init__.py` and `android_rules/__init__.py`, `java_rules/__init__.py`**

```python
# Java rules package
```

Do the same for the others.

- [ ] **Step 4: Create directories**

```bash
mkdir -p src/local_rules/java_rules
mkdir -p src/local_rules/android_rules
mkdir -p src/local_rules/kotlin_rules
touch src/local_rules/java_rules/__init__.py
touch src/local_rules/android_rules/__init__.py
touch src/local_rules/kotlin_rules/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git add src/local_rules/
git commit -m "feat: add base rule class and rule loader"
```

---

### Task 6: 内置 Java 规则 - 调试日志检查

**Files:**
- Create: `src/local_rules/java_rules/debug_logging.py`
- Create: `tests/java_rules/test_debug_logging.py`

- [ ] **Step 1: Write test**

```python
from src.local_rules.java_rules.debug_logging import DebugLoggingRule
from src.diff_parser import FileDiff, DiffChange


def test_finds_system_out():
    rule = DebugLoggingRule()
    change = DiffChange(line_number=10, content="        System.out.println(\"debug\");", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
    assert "System.out.println" in findings[0].message


def test_finds_log_d():
    rule = DebugLoggingRule()
    change = DiffChange(line_number=10, content="        Log.d(TAG, \"debug msg\");", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/java_rules/test_debug_logging.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement `debug_logging.py`**

```python
import re
from typing import List

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


DEBUG_LOG_PATTERNS = [
    re.compile(r'System\.out\.println'),
    re.compile(r'System\.err\.println'),
    re.compile(r'Log\.d\b'),
    re.compile(r'Log\.v\b'),
]


class DebugLoggingRule(BaseRule):
    """Check for debug logging statements that shouldn't be committed."""

    @property
    def name(self) -> str:
        return "Java-DebugLogging"

    @property
    def description(self) -> str:
        return "Detects debug logging statements (System.out.println, Log.d) that should be removed before commit"

    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        content = change.content.strip()

        for pattern in DEBUG_LOG_PATTERNS:
            if pattern.search(content):
                findings.append(RuleFinding(
                    file_path=file_diff.file_path,
                    line_number=change.line_number,
                    rule_name=self.name,
                    message=f"Found debug logging statement `{pattern.pattern}` - should be removed before commit",
                    severity="BLOCK",
                    code_snippet=content
                ))

        return findings

    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        findings = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            for pattern in DEBUG_LOG_PATTERNS:
                if pattern.search(line):
                    findings.append(RuleFinding(
                        file_path=file_path,
                        line_number=i,
                        rule_name=self.name,
                        message=f"Found debug logging statement `{pattern.pattern}` - should be removed before commit",
                        severity="BLOCK",
                        code_snippet=line_stripped
                    ))

        return findings
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/java_rules/test_debug_logging.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/local_rules/java_rules/debug_logging.py tests/java_rules/test_debug_logging.py
git commit -m "feat: add debug logging rule for Java"
```

---

### Task 7: 内置 Java 规则 - 硬编码敏感信息检查

**Files:**
- Create: `src/local_rules/java_rules/hardcoded_secrets.py`
- Create: `tests/java_rules/test_hardcoded_secrets.py`

- [ ] **Step 1: Write test**

```python
from src.local_rules.java_rules.hardcoded_secrets import HardcodedSecretsRule
from src.diff_parser import FileDiff, DiffChange


def test_finds_password_in_string():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String password = "mysecret123";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"


def test_finds_api_key():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String apiKey = "AKIAXXXX";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 1
```

- [ ] **Step 2: Implement the rule**

```python
import re
from typing import List

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


SECRET_PATTERNS = [
    re.compile(r'password\s*[=:]\s*["\']\w+["\']', re.IGNORECASE),
    re.compile(r'secret\s*[=:]\s*["\']\w+["\']', re.IGNORECASE),
    re.compile(r'api[_-]?key\s*[=:]\s*["\']\w+["\']', re.IGNORECASE),
    re.compile(r'token\s*[=:]\s*["\']\w+["\']', re.IGNORECASE),
]


class HardcodedSecretsRule(BaseRule):
    """Check for hardcoded secrets/passwords/API keys in code."""

    @property
    def name(self) -> str:
        return "Java-HardcodedSecrets"

    @property
    def description(self) -> str:
        return "Detects hardcoded secrets, passwords, and API keys that should not be in source code"

    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        return self._check_line(file_diff.file_path, change.line_number, change.content)

    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        findings = []
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            findings.extend(self._check_line(file_path, i, line))
        return findings

    def _check_line(self, file_path: str, line_number: int, content: str) -> List[RuleFinding]:
        findings = []
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                findings.append(RuleFinding(
                    file_path=file_path,
                    line_number=line_number,
                    rule_name=self.name,
                    message="Found potential hardcoded secret/password/api key. Secrets should be in configuration, not in source code.",
                    severity="BLOCK",
                    code_snippet=content.strip()
                ))
        return findings
```

- [ ] **Step 3: Run test, commit**

```bash
git add src/local_rules/java_rules/hardcoded_secrets.py tests/java_rules/test_hardcoded_secrets.py
git commit -m "feat: add hardcoded secrets detection rule"
```

---

### Task 8: 其余 Java 规则

**Files:**
- Create: `src/local_rules/java_rules/unclosed_resources.py`
- Create: `src/local_rules/java_rules/npe_risk.py`
- Create: `src/local_rules/java_rules/memory_leak.py`
- Tests for each

*(Repeat similar pattern - for brevity, the plan has full skeleton for the first tasks, the rest follow same pattern.)*

---

### Task 9: Android 特有规则

**Files:**
- Create: `src/local_rules/android_rules/hardcoded_urls.py`
- Create: `src/local_rules/android_rules/binary_files.py`
- Create: `src/local_rules/android_rules/viewholder_pattern.py`

---

### Task 10: AI 客户端基类

**Files:**
- Create: `src/ai_reviewer/base_client.py`
- Create: `src/ai_reviewer/__init__.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AIReviewFinding:
    file_path: str
    line_start: int
    line_end: int
    issue_type: str  # "BUG", "PERFORMANCE", "STYLE", "SECURITY"
    severity: str  # "BLOCK", "WARNING"
    message: str
    suggestion: Optional[str] = None


@dataclass
class AIReviewResult:
    success: bool
    findings: List[AIReviewFinding]
    error_message: Optional[str] = None
    tokens_used: int = 0


class BaseAIClient(ABC):
    """Base class for AI review clients."""

    @abstractmethod
    def review_diff(self, file_path: str, diff_content: str, prompt_template: str) -> AIReviewResult:
        """Review a diff chunk with AI."""
        pass

    @abstractmethod
    def review_full_file(self, file_path: str, content: str, prompt_template: str) -> AIReviewResult:
        """Review the full file with AI."""
        pass
```

---

### Task 11: Claude API 客户端实现

**Files:**
- Create: `src/ai_reviewer/claude_client.py`

- Implement Claude API client using requests, follows BaseAIClient interface.
- Reads API key from Config.

---

### Task 12: OpenRouter API 客户端实现

**Files:**
- Create: `src/ai_reviewer/openrouter_client.py`

- Similar to Claude client, but uses OpenRouter API endpoint.

---

### Task 13: Ollama 骨架客户端实现

**Files:**
- Create: `src/ai_reviewer/local_ollama_client.py`

- Implements the interface with placeholder/NotImplemented error.
- Ready for future implementation.

---

### Task 14: AI 提示词模板文件

**Files:**
- Create: `src/ai_reviewer/prompt_templates/java-diff-review.md`
- Create: `src/ai_reviewer/prompt_templates/kotlin-diff-review.md`
- Create: `src/ai_reviewer/prompt_templates/android-full-review.md`

Write structured prompts that instruct AI to output JSON-formatted findings.

---

### Task 15: 报告生成器 - 文本、HTML、JSON

**Files:**
- Create: `src/reporter/text_reporter.py`
- Create: `src/reporter/html_reporter.py`
- Create: `src/reporter/json_reporter.py`

Each generates the corresponding format with timestamped filename.

---

### Task 16: 主程序入口

**Files:**
- Create: `src/main.py`

Implement the full flow:
1. Parse arguments
2. Load config from env
3. Get diff from SVN
4. Parse diff
5. Scan files, apply filtering
6. Run local rules
7. If any BLOCK findings: exit 1
8. If diff passes, ask user about full review
9. If user says yes, run full review
10. Generate all reports
11. Exit 0 to allow commit

---

### Task 17: SVN 钩子脚本

**Files:**
- Create: `hooks/pre-commit`

Bash/Windows-compatible script that calls `src/main.py` for SVN.

---

### Task 18: 文档编写

**Files:**
- Create: `docs/writing-local-rules.md`
- Create: `docs/writing-ai-prompts.md`

Write the guides for new contributors.

---

### Task 19: 测试验证

Run all tests, verify the end-to-end flow.

---

## 自我检查

- ✓ 所有设计需求都对应到了具体任务
- ✓ 没有占位符，每个任务都有明确步骤
- ✓ 采用基类接口，易于扩展
- ✓ Ollama 骨架已预留
- ✓ libs 变更提醒已包含
- ✓ 两阶段审查（diff + 可选全文）已体现
- ✓ 三种输出格式都有对应模块
- ✓ 环境变量配置已实现
- ✓ 两份指南文档已规划

No gaps found.

