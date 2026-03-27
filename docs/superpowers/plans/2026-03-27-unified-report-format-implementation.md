# 统一报告格式实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现代码审查工具的统一报告格式，采用五列固定格式，使用AI进行问题类型分类和修复建议生成。

**Architecture:** 新增 AI 处理模块，将原始发现转换为统一格式 `UnifiedFinding`，重构三个报告生成器输出表格形式。

**Tech Stack:** Python, Anthropic API, Markdown, HTML, JSON

---

## 文件结构规划

### 将创建的文件：
- `src/reporter/unified_finding.py` - 统一格式数据类
- `src/reporter/unified_finding_processor.py` - AI 处理模块
- `tests/reporter/test_unified_finding.py` - 单元测试
- `tests/reporter/test_unified_finding_processor.py` - 单元测试

### 将修改的文件：
- `src/reporter/text_reporter.py` - 重构为 Markdown 表格输出
- `src/reporter/html_reporter.py` - 重构为 Bootstrap 表格输出
- `src/reporter/json_reporter.py` - 重构为统一格式输出
- `src/reporter/base_reporter.py` - 调整集成逻辑
- `src/main.py` - 集成到主流程

---

## 任务分解

### Task 1: 创建 UnifiedFinding 数据类

**Files:**
- Create: `src/reporter/unified_finding.py`
- Test: `tests/reporter/test_unified_finding.py`

- [ ] **Step 1: 创建数据类**
```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class UnifiedFinding:
    """统一格式的代码审查发现类"""
    priority: str       # 严重/一般/轻微
    issue_type: str     # 内存泄露/超时处理不足/安全隐患等（由AI分析）
    location: str       # 文件路径:行号
    description: str    # 问题详细说明
    suggestion: str     # 修复建议（由AI生成）

    def to_dict(self) -> dict:
        """转换为字典格式，用于报告生成"""
        return {
            "优先级": self.priority,
            "问题类型": self.issue_type,
            "位置": self.location,
            "说明": self.description,
            "修复建议": self.suggestion
        }
```

- [ ] **Step 2: 编写单元测试**
```python
import pytest
from src.reporter.unified_finding import UnifiedFinding


def test_unified_finding_creation():
    finding = UnifiedFinding(
        priority="严重",
        issue_type="内存泄露",
        location="MainActivity.java:120",
        description="Handler 持有外部类引用",
        suggestion="使用静态内部类 + WeakReference"
    )

    assert finding.priority == "严重"
    assert finding.issue_type == "内存泄露"
    assert finding.location == "MainActivity.java:120"
    assert finding.description == "Handler 持有外部类引用"
    assert finding.suggestion == "使用静态内部类 + WeakReference"


def test_unified_finding_to_dict():
    finding = UnifiedFinding(
        priority="一般",
        issue_type="超时处理不足",
        location="ApiClient.java:85",
        description="网络请求超时设置过短",
        suggestion="增加超时时间到 30 秒"
    )

    data = finding.to_dict()

    assert data["优先级"] == "一般"
    assert data["问题类型"] == "超时处理不足"
    assert data["位置"] == "ApiClient.java:85"
    assert data["说明"] == "网络请求超时设置过短"
    assert data["修复建议"] == "增加超时时间到 30 秒"
```

- [ ] **Step 3: 运行测试**
```bash
pytest tests/reporter/test_unified_finding.py -v
```
Expected: 2 tests PASS

- [ ] **Step 4: 提交**
```bash
git add src/reporter/unified_finding.py tests/reporter/test_unified_finding.py
git commit -m "feat: add UnifiedFinding data class"
```

---

### Task 2: 创建统一发现处理器

**Files:**
- Create: `src/reporter/unified_finding_processor.py`
- Test: `tests/reporter/test_unified_finding_processor.py`

- [ ] **Step 1: 实现处理器类**
```python
import logging
from typing import List, Optional

from src.diff_parser import DiffChange, FileDiff
from src.ai_reviewer.base_client import AIReviewFinding
from src.local_rules.base_rule import RuleFinding
from src.reporter.unified_finding import UnifiedFinding


logger = logging.getLogger(__name__)


class UnifiedFindingProcessor:
    """负责将原始发现转换为统一格式的处理器"""

    def __init__(self, config=None):
        self.config = config

    def convert_rule_finding(self, finding: RuleFinding) -> UnifiedFinding:
        """将 RuleFinding 转换为 UnifiedFinding"""
        # 优先级映射
        if finding.severity.upper() == "BLOCK":
            priority = "严重"
        else:
            priority = "一般"

        # 位置格式：文件路径:行号
        location = f"{finding.file_path}:{finding.line_number}"

        return UnifiedFinding(
            priority=priority,
            issue_type=finding.rule_name,  # 先使用规则名称，后期可替换为AI分析
            location=location,
            description=finding.message,
            suggestion=""  # 本地规则暂时没有建议
        )

    def convert_ai_finding(self, finding: AIReviewFinding) -> UnifiedFinding:
        """将 AIReviewFinding 转换为 UnifiedFinding"""
        # 优先级映射
        if finding.severity.upper() == "BLOCK":
            priority = "严重"
        elif finding.severity.upper() == "WARNING":
            priority = "一般"
        else:
            priority = "轻微"

        # 位置格式：文件路径:行号范围
        location = f"{finding.file_path}:{finding.line_start}-{finding.line_end}"

        return UnifiedFinding(
            priority=priority,
            issue_type=finding.issue_type,
            location=location,
            description=finding.message,
            suggestion=finding.suggestion if finding.suggestion else ""
        )

    def process_all(self,
                   local_findings: List[RuleFinding],
                   ai_findings: List[AIReviewFinding]) -> List[UnifiedFinding]:
        """处理所有原始发现，转换为统一格式"""
        findings: List[UnifiedFinding] = []

        for finding in local_findings:
            try:
                unified = self.convert_rule_finding(finding)
                findings.append(unified)
            except Exception as e:
                logger.warning(f"Failed to convert rule finding: {e}")

        for finding in ai_findings:
            try:
                unified = self.convert_ai_finding(finding)
                findings.append(unified)
            except Exception as e:
                logger.warning(f"Failed to convert AI finding: {e}")

        return findings
```

- [ ] **Step 2: 编写单元测试**
```python
import pytest
from src.reporter.unified_finding_processor import UnifiedFindingProcessor
from src.ai_reviewer.base_client import AIReviewFinding
from src.local_rules.base_rule import RuleFinding


def test_convert_rule_finding_block():
    processor = UnifiedFindingProcessor()
    finding = RuleFinding(
        file_path="MainActivity.java",
        line_number=120,
        rule_name="memory_leak",
        message="Handler 持有外部类引用",
        severity="BLOCK"
    )

    result = processor.convert_rule_finding(finding)

    assert result.priority == "严重"
    assert result.issue_type == "memory_leak"
    assert result.location == "MainActivity.java:120"
    assert result.description == "Handler 持有外部类引用"
    assert result.suggestion == ""


def test_convert_rule_finding_warning():
    processor = UnifiedFindingProcessor()
    finding = RuleFinding(
        file_path="ApiClient.java",
        line_number=85,
        rule_name="timeout_issue",
        message="网络请求超时设置过短",
        severity="WARNING"
    )

    result = processor.convert_rule_finding(finding)

    assert result.priority == "一般"
    assert result.issue_type == "timeout_issue"
    assert result.location == "ApiClient.java:85"
    assert result.description == "网络请求超时设置过短"
    assert result.suggestion == ""


def test_convert_ai_finding():
    processor = UnifiedFindingProcessor()
    finding = AIReviewFinding(
        file_path="Utils.java",
        line_start=42,
        line_end=50,
        issue_type="代码风格",
        severity="WARNING",
        message="未使用 try-with-resources",
        suggestion="改用 try-with-resources 语法"
    )

    result = processor.convert_ai_finding(finding)

    assert result.priority == "一般"
    assert result.issue_type == "代码风格"
    assert result.location == "Utils.java:42-50"
    assert result.description == "未使用 try-with-resources"
    assert result.suggestion == "改用 try-with-resources 语法"
```

- [ ] **Step 3: 运行测试**
```bash
pytest tests/reporter/test_unified_finding_processor.py -v
```
Expected: 3 tests PASS

- [ ] **Step 4: 提交**
```bash
git add src/reporter/unified_finding_processor.py tests/reporter/test_unified_finding_processor.py
git commit -m "feat: add UnifiedFindingProcessor"
```

---

### Task 3: 重构 TextReporter

**Files:**
- Modify: `src/reporter/text_reporter.py`
- Test: `tests/reporter/test_text_reporter.py`

- [ ] **Step 1: 重构为 Markdown 表格输出**
```python
import datetime
from typing import List, Dict, Any
from src.reporter.unified_finding import UnifiedFinding
from .base_reporter import BaseReporter


class TextReporter(BaseReporter):
    """生成代码审查结果的 Markdown 表格格式文本报告。"""

    def generate_report(self,
                       findings: List[UnifiedFinding],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """生成 Markdown 格式报告内容。"""
        timestamp = meta.get('timestamp', datetime.datetime.now().isoformat())
        mode = meta.get('mode', 'unknown')
        file_count = meta.get('file_count', 0)
        has_blocking = any(finding.priority == "严重" for finding in findings)
        libs_change = meta.get('libs_change', False)

        report = []
        report.append("=" * 80)
        report.append("CODE REVIEW REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {timestamp}")
        report.append(f"Mode: {mode}")
        report.append(f"Files processed: {file_count}")
        report.append(f"Blocking issues found: {'YES' if has_blocking else 'NO'}")
        report.append(f"Library changes detected: {'YES' if libs_change else 'NO'}")
        if libs_reminder:
            report.append(f"Library reminder: {libs_reminder}")
        report.append("=" * 80)
        report.append("")

        # 表格标题
        if findings:
            report.append(f"FINDINGS: {len(findings)} issues")
            report.append("-" * 80)

            # 表格头部
            report.append("| 优先级 | 问题类型 | 位置 | 说明 | 修复建议 |")
            report.append("|--------|---------|------|------|----------|")

            # 表格内容
            for finding in findings:
                # 转义表格内容中的 | 字符
                description = finding.description.replace("|", "\\|")
                suggestion = finding.suggestion.replace("|", "\\|") if finding.suggestion else ""

                report.append(f"| {finding.priority} | {finding.issue_type} | {finding.location} | {description} | {suggestion} |")

            report.append("")

        # 总结
        report.append(f"\n{'=' * 80}")
        report.append(f"SUMMARY: Total issues found - {len(findings)}")
        report.append(f"  - 严重: {sum(1 for f in findings if f.priority == '严重')}")
        report.append(f"  - 一般: {sum(1 for f in findings if f.priority == '一般')}")
        report.append(f"  - 轻微: {sum(1 for f in findings if f.priority == '轻微')}")
        report.append(f"{'=' * 80}")

        return "\n".join(report)

    def _get_file_extension(self) -> str:
        """获取文本报告的文件扩展名。"""
        return "txt"
```

- [ ] **Step 2: 编写单元测试**
```python
import pytest
from src.reporter.text_reporter import TextReporter
from src.reporter.unified_finding import UnifiedFinding


def test_text_reporter_generation():
    reporter = TextReporter()
    findings = [
        UnifiedFinding(
            priority="严重",
            issue_type="内存泄露",
            location="MainActivity.java:120",
            description="Handler 持有外部类引用",
            suggestion="使用静态内部类 + WeakReference"
        ),
        UnifiedFinding(
            priority="一般",
            issue_type="超时处理不足",
            location="ApiClient.java:85",
            description="网络请求超时设置过短",
            suggestion="增加超时时间到 30 秒"
        )
    ]

    report = reporter.generate_report(findings, {})

    assert "内存泄露" in report
    assert "MainActivity.java:120" in report
    assert "超时处理不足" in report
    assert "ApiClient.java:85" in report


def test_text_reporter_headers():
    reporter = TextReporter()
    report = reporter.generate_report([], {})

    assert "CODE REVIEW REPORT" in report
    assert "Generated:" in report
    assert "Mode:" in report
```

- [ ] **Step 3: 运行测试**
```bash
pytest tests/reporter/test_text_reporter.py -v
```
Expected: 2 tests PASS

- [ ] **Step 4: 提交**
```bash
git add src/reporter/text_reporter.py tests/reporter/test_text_reporter.py
git commit -m "refactor:重构TextReporter输出Markdown表格"
```

---

### Task 4: 重构 HTMLReporter

**Files:**
- Modify: `src/reporter/html_reporter.py`
- Test: `tests/reporter/test_html_reporter.py`

- [ ] **Step 1: 重构为 Bootstrap 表格输出**
```python
import datetime
from typing import List, Dict, Any
from src.reporter.unified_finding import UnifiedFinding
from .base_reporter import BaseReporter


class HTMLReporter(BaseReporter):
    """生成代码审查结果的 HTML 格式报告。"""

    def generate_report(self,
                       findings: List[UnifiedFinding],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """生成 HTML 报告内容。"""
        timestamp = meta.get('timestamp', datetime.datetime.now().isoformat())
        mode = meta.get('mode', 'unknown')
        file_count = meta.get('file_count', 0)
        has_blocking = any(finding.priority == "严重" for finding in findings)
        libs_change = meta.get('libs_change', False)

        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang=\"zh-CN\">")
        html.append("<head>")
        html.append("    <meta charset=\"UTF-8\">")
        html.append("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
        html.append("    <title>代码审查报告</title>")
        html.append("    <link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css\">")
        html.append("    <style>")
        html.append("        body { font-family: 'Segoe UI', sans-serif; margin: 20px; }")
        html.append("        .report-header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }")
        html.append("        .report-header h1 { color: #333; font-size: 24px; margin: 0; }")
        html.append("        .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 14px; }")
        html.append("        .severity-high { background-color: #dc3545; color: white; }")
        html.append("        .severity-medium { background-color: #ffc107; color: black; }")
        html.append("        .severity-low { background-color: #17a2b8; color: white; }")
        html.append("    </style>")
        html.append("</head>")
        html.append("<body>")
        html.append("<div class=\"container\">")

        # 报告头部
        html.append("<div class=\"report-header\">")
        html.append("    <h1>代码审查报告</h1>")
        html.append("    <div style=\"margin-top: 10px;\">")
        html.append(f"        <p style=\"margin: 5px 0;\">生成时间: {timestamp}</p>")
        html.append(f"        <p style=\"margin: 5px 0;\">模式: {mode}</p>")
        html.append(f"        <p style=\"margin: 5px 0;\">处理文件数: {file_count}</p>")
        html.append(f"        <p style=\"margin: 5px 0;\">阻塞问题: {'<span class=\"status-badge severity-high\">严重</span>' if has_blocking else '无'}</p>")
        html.append(f"        <p style=\"margin: 5px 0;\">库变更: {'有' if libs_change else '无'}</p>")
        if libs_reminder:
            html.append(f"        <p style=\"margin: 5px 0;\">库提醒: {libs_reminder}</p>")
        html.append("    </div>")
        html.append("</div>")

        # 表格内容
        if findings:
            html.append(f"<h2>发现的问题 ({len(findings)} 个)</h2>")
            html.append("<div class=\"table-responsive\">")
            html.append("<table class=\"table table-bordered table-hover\">")
            html.append("    <thead class=\"thead-light\">")
            html.append("        <tr>")
            html.append("            <th>优先级</th>")
            html.append("            <th>问题类型</th>")
            html.append("            <th>位置</th>")
            html.append("            <th>说明</th>")
            html.append("            <th>修复建议</th>")
            html.append("        </tr>")
            html.append("    </thead>")
            html.append("    <tbody>")

            for finding in findings:
                severity_class = {
                    "严重": "danger",
                    "一般": "warning",
                    "轻微": "info"
                }[finding.priority]

                badge_class = {
                    "严重": "severity-high",
                    "一般": "severity-medium",
                    "轻微": "severity-low"
                }[finding.priority]

                html.append("        <tr class=\"table-" + severity_class + "\">")
                html.append(f"            <td><span class=\"status-badge {badge_class}\">{finding.priority}</span></td>")
                html.append(f"            <td>{finding.issue_type}</td>")
                html.append(f"            <td>{finding.location}</td>")
                html.append(f"            <td>{finding.description}</td>")
                html.append(f"            <td>{finding.suggestion if finding.suggestion else '-'}</td>")
                html.append("        </tr>")

            html.append("    </tbody>")
            html.append("</table>")
            html.append("</div>")
        else:
            html.append("<div class=\"alert alert-success\">")
            html.append("    <h4 class=\"alert-heading\">审查通过！</h4>")
            html.append("    <p>未发现需要处理的问题。</p>")
            html.append("</div>")

        # 总结
        html.append("<div style=\"margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;\">")
        html.append("<h3>问题统计</h3>")
        html.append(f"<p>严重: {sum(1 for f in findings if f.priority == '严重')}</p>")
        html.append(f"<p>一般: {sum(1 for f in findings if f.priority == '一般')}</p>")
        html.append(f"<p>轻微: {sum(1 for f in findings if f.priority == '轻微')}</p>")
        html.append("</div>")

        html.append("</div>")
        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def _get_file_extension(self) -> str:
        """获取 HTML 报告的文件扩展名。"""
        return "html"
```

- [ ] **Step 2: 编写单元测试**
```python
import pytest
from src.reporter.html_reporter import HTMLReporter
from src.reporter.unified_finding import UnifiedFinding


def test_html_reporter_generation():
    reporter = HTMLReporter()
    findings = [
        UnifiedFinding(
            priority="严重",
            issue_type="内存泄露",
            location="MainActivity.java:120",
            description="Handler 持有外部类引用",
            suggestion="使用静态内部类 + WeakReference"
        )
    ]

    report = reporter.generate_report(findings, {})

    assert "内存泄露" in report
    assert "MainActivity.java:120" in report
    assert '<table class="table' in report


def test_html_reporter_css_styles():
    reporter = HTMLReporter()
    report = reporter.generate_report([], {})

    assert "bootstrap" in report.lower()
    assert "stylesheet" in report
```

- [ ] **Step 3: 运行测试**
```bash
pytest tests/reporter/test_html_reporter.py -v
```
Expected: 2 tests PASS

- [ ] **Step 4: 提交**
```bash
git add src/reporter/html_reporter.py tests/reporter/test_html_reporter.py
git commit -m "refactor:重构HTMLReporter输出Bootstrap表格"
```

---

### Task 5: 重构 JSONReporter

**Files:**
- Modify: `src/reporter/json_reporter.py`
- Test: `tests/reporter/test_json_reporter.py`

- [ ] **Step 1: 重构为统一格式输出**
```python
import datetime
import json
from typing import List, Dict, Any
from src.reporter.unified_finding import UnifiedFinding
from .base_reporter import BaseReporter


class JSONReporter(BaseReporter):
    """生成代码审查结果的 JSON 格式报告。"""

    def generate_report(self,
                       findings: List[UnifiedFinding],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """生成 JSON 格式报告内容。"""
        timestamp = meta.get('timestamp', datetime.datetime.now().isoformat())
        mode = meta.get('mode', 'unknown')
        file_count = meta.get('file_count', 0)
        has_blocking = any(finding.priority == "严重" for finding in findings)
        libs_change = meta.get('libs_change', False)

        report_data = {
            "generated": timestamp,
            "mode": mode,
            "file_count": file_count,
            "has_blocking": has_blocking,
            "libs_change": libs_change,
            "libs_reminder": libs_reminder,
            "findings": [finding.to_dict() for finding in findings],
            "statistics": {
                "total": len(findings),
                "严重": sum(1 for f in findings if f.priority == "严重"),
                "一般": sum(1 for f in findings if f.priority == "一般"),
                "轻微": sum(1 for f in findings if f.priority == "轻微")
            }
        }

        return json.dumps(report_data, ensure_ascii=False, indent=2)

    def _get_file_extension(self) -> str:
        """获取 JSON 报告的文件扩展名。"""
        return "json"
```

- [ ] **Step 2: 编写单元测试**
```python
import pytest
from src.reporter.json_reporter import JSONReporter
from src.reporter.unified_finding import UnifiedFinding


def test_json_reporter_generation():
    reporter = JSONReporter()
    findings = [
        UnifiedFinding(
            priority="严重",
            issue_type="内存泄露",
            location="MainActivity.java:120",
            description="Handler 持有外部类引用",
            suggestion="使用静态内部类 + WeakReference"
        )
    ]

    report = reporter.generate_report(findings, {})

    assert "内存泄露" in report
    assert "MainActivity.java:120" in report
    assert "静态内部类" in report


def test_json_reporter_statistics():
    reporter = JSONReporter()
    findings = [
        UnifiedFinding(priority="严重", issue_type="a", location="", description="", suggestion=""),
        UnifiedFinding(priority="一般", issue_type="b", location="", description="", suggestion=""),
        UnifiedFinding(priority="一般", issue_type="c", location="", description="", suggestion=""),
        UnifiedFinding(priority="轻微", issue_type="d", location="", description="", suggestion="")
    ]

    report = reporter.generate_report(findings, {})

    assert '"严重": 1' in report
    assert '"一般": 2' in report
    assert '"轻微": 1' in report
```

- [ ] **Step 3: 运行测试**
```bash
pytest tests/reporter/test_json_reporter.py -v
```
Expected: 2 tests PASS

- [ ] **Step 4: 提交**
```bash
git add src/reporter/json_reporter.py tests/reporter/test_json_reporter.py
git commit -m "refactor:重构JSONReporter输出统一格式"
```

---

### Task 6: 调整 BaseReporter 集成逻辑

**Files:**
- Modify: `src/reporter/base_reporter.py`
- Test: `tests/reporter/test_base_reporter.py`

- [ ] **Step 1: 调整集成逻辑**
```python
import os
import datetime
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from src.reporter.unified_finding import UnifiedFinding
from src.reporter.unified_finding_processor import UnifiedFindingProcessor


class BaseReporter(ABC):
    """所有报告生成器的基础抽象类。"""

    def __init__(self, output_dir: str = "code-review-output"):
        """使用输出目录初始化报告生成器。"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.processor = UnifiedFindingProcessor()

    def _get_timestamp(self, meta: Dict[str, Any]) -> datetime.datetime:
        """从元数据获取时间戳，或使用当前时间。"""
        timestamp = meta.get('timestamp', datetime.datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.fromisoformat(timestamp)
        return timestamp

    def _format_timestamp(self, timestamp: Optional[datetime.datetime] = None) -> str:
        """为文件名格式化时间戳。"""
        if timestamp is None:
            timestamp = datetime.datetime.now()
        return timestamp.strftime('%Y%m%d-%H%M%S')

    @abstractmethod
    def generate_report(self,
                       findings: List[UnifiedFinding],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """生成报告内容的抽象方法。"""
        pass

    def generate(self,
                local_findings: List[Any],
                ai_findings: List[Any],
                meta: Dict[str, Any],
                config=None) -> str:
        """从所有发现（本地和AI）生成报告并写入文件。"""

        # 转换为统一格式
        findings = self.processor.process_all(local_findings, ai_findings)

        return self.write_report(findings, meta)

    def write_report(self,
                    findings: List[UnifiedFinding],
                    meta: Dict[str, Any],
                    libs_reminder: str = "") -> str:
        """生成报告并写入输出文件。"""
        content = self.generate_report(findings, meta, libs_reminder)

        timestamp = self._get_timestamp(meta)
        filename = f"review-result-{self._format_timestamp(timestamp)}.{self._get_file_extension()}"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    @abstractmethod
    def _get_file_extension(self) -> str:
        """获取报告格式文件扩展名的抽象方法。"""
        pass
```

- [ ] **Step 2: 更新集成测试**
```python
import pytest
from src.reporter.base_reporter import BaseReporter
from src.reporter.unified_finding import UnifiedFinding
from src.reporter.text_reporter import TextReporter


class MockReporter(BaseReporter):
    """用于测试的模拟报告生成器。"""

    def generate_report(self, findings, meta, libs_reminder=""):
        return f"Report with {len(findings)} findings"

    def _get_file_extension(self):
        return "txt"


def test_base_reporter_generation():
    reporter = MockReporter()
    findings = [
        UnifiedFinding(
            priority="严重",
            issue_type="内存泄露",
            location="MainActivity.java:120",
            description="Handler 持有外部类引用",
            suggestion="使用静态内部类 + WeakReference"
        )
    ]

    result = reporter.write_report(findings, {})

    assert "review-result" in result
    assert ".txt" in result
```

- [ ] **Step 3: 运行测试**
```bash
pytest tests/reporter/test_base_reporter.py -v
```
Expected: 1 test PASS

- [ ] **Step 4: 提交**
```bash
git add src/reporter/base_reporter.py tests/reporter/test_base_reporter.py
git commit -m "refactor:调整BaseReporter集成逻辑"
```

---

### Task 7: 集成到主程序流程

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: 更新主流程集成**
```python
    # 8. 生成报告
    if has_blocking:
        logging.info("发现阻塞问题，生成报告并阻止提交")
        report_path = generate_report(
            local_findings, ai_findings, {
                "mode": "diff-review",
                "file_count": len(file_scanner.file_diffs),
                "timestamp": str(datetime.now()),
                "has_blocking": True,
                "libs_change": len(file_scanner.libs_changes) > 0
            },
            libs_reminder
        )
        print(f"代码审查失败！详细报告: {report_path}")
        return False

    # 8.2 选择完整审查
    if args.full_review or prompt_full_review():
        logging.info("执行完整审查")
        full_local_findings = run_full_review(local_rules)
        full_ai_findings = run_ai_full_review(ai_clients, file_scanner.source_files)

        all_local = local_findings + full_local_findings
        all_ai = ai_findings + full_ai_findings

        report_path = generate_report(
            all_local, all_ai, {
                "mode": "full-review",
                "file_count": len(file_scanner.file_diffs),
                "timestamp": str(datetime.now()),
                "has_blocking": False,
                "libs_change": len(file_scanner.libs_changes) > 0
            },
            libs_reminder
        )

        print(f"完整审查完成！详细报告: {report_path}")
```

- [ ] **Step 2: 更新报告生成函数**
```python
def generate_report(local_findings: List[RuleFinding],
                   ai_findings: List[AIReviewFinding],
                   meta: dict,
                   libs_reminder: str = "") -> str:
    """生成所有格式的报告并写入文件。"""

    # 三个报告实例
    reporters = [
        TextReporter(),
        HTMLReporter(),
        JSONReporter()
    ]

    for reporter in reporters:
        reporter.write_report(local_findings, ai_findings, meta, libs_reminder)

    # 返回HTML报告路径
    html_reporter = HTMLReporter()
    return html_reporter.write_report(local_findings, ai_findings, meta, libs_reminder)
```

- [ ] **Step 3: 运行测试**
```bash
pytest tests/main/test_integration.py -v
```
Expected: All integration tests PASS

- [ ] **Step 4: 提交**
```bash
git add src/main.py
git commit -m "feat:集成统一格式报告到主流程"
```

---

### Task 8: 集成到系统流程

**Files:**
- Modify: `src/main.py`
- Modify: `src/reporter/__init__.py`

- [ ] **Step 1: 更新主程序入口**
```python
from src.reporter.text_reporter import TextReporter
from src.reporter.html_reporter import HTMLReporter
from src.reporter.json_reporter import JSONReporter
from src.reporter.base_reporter import BaseReporter
```

- [ ] **Step 2: 更新 reporter __init__.py**
```python
"""Reporter module for generating code review reports in various formats."""

from .base_reporter import BaseReporter
from .text_reporter import TextReporter
from .html_reporter import HTMLReporter
from .json_reporter import JSONReporter
from .unified_finding import UnifiedFinding
from .unified_finding_processor import UnifiedFindingProcessor

__all__ = [
    "BaseReporter",
    "TextReporter",
    "HTMLReporter",
    "JSONReporter",
    "UnifiedFinding",
    "UnifiedFindingProcessor"
]
```

- [ ] **Step 3: 运行完整测试套件**
```bash
pytest tests/ -v
```
Expected: All 40+ tests PASS

- [ ] **Step 4: 提交**
```bash
git add src/reporter/__init__.py
git commit -m "refactor:更新reporter模块导出"
```

---

### Task 9: 更新 README.md 说明文档

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新报告格式说明**

更新以下内容：
1. 核心特点 - 更新"多格式报告"为"统一表格格式报告"
2. 报告示例 - 更新为五列表格格式
3. 报告格式说明 - 详细说明新的表格结构
4. 规则分级 - 更新为"严重/一般/轻微"

修改的关键部分：

```markdown
### 核心特点

- **自动化审查流程**：作为 SVN pre-commit 钩子运行，无需人工干预
- **双重审查机制**：结合本地静态规则检查和 AI 智能分析
- **统一表格格式**：所有发现统一整理为五列表格格式（优先级/问题类型/位置/说明/修复建议）
- **AI 智能分析**：AI 自动分析问题类型并提供修复建议
- **智能过滤**：自动忽略 build/、generated/ 等自动生成目录
- **用户友好**：图形化界面询问是否需要全文 AI 审查
- **多格式报告**：支持文本、HTML 和 JSON 三种报告格式
- **易于扩展**：模块化架构，支持新增本地规则和 AI 提供商
```

```markdown
### 报告示例

**文本报告示例（部分）：**

```
================================================================================
CODE REVIEW REPORT
================================================================================
Generated: 2026-03-27T10:30:00.123456
Mode: diff-review
Files processed: 3
Blocking issues found: YES
Library changes detected: NO
================================================================================

FINDINGS: 3 issues
--------------------------------------------------------------------------------

| 优先级 | 问题类型 | 位置 | 说明 | 修复建议 |
|--------|---------|------|------|----------|
| 严重 | 调试日志残留 | MainActivity.java:45 | 发现调试日志残留: System.out.println("Debug info") | 删除调试日志或使用正式日志框架 |
| 一般 | 超时处理不足 | ApiClient.java:85 | 网络请求超时设置过短 | 增加超时时间到 30 秒 |
| 轻微 | 代码风格 | Utils.java:42 | 未使用 try-with-resources | 改用 try-with-resources 语法 |

================================================================================
SUMMARY: Total issues found - 3
  - 严重: 1
  - 一般: 1
  - 轻微: 1
================================================================================
```
```

```markdown
## 报告格式说明

### 统一表格格式

所有发现统一整理为五列表格格式，包含以下列：

| 列名 | 说明 |
|------|------|
| **优先级** | 严重/一般/轻微（严重需立即修复，一般建议修复，轻微可后续修复） |
| **问题类型** | 内存泄露/超时处理不足/安全隐患/代码风格等（由AI分析分类） |
| **位置** | 文件路径:行号（如：MainActivity.java:120） |
| **说明** | 问题的详细描述 |
| **修复建议** | AI 生成的修复建议 |

### 优先级说明

| 级别 | 说明 | 对提交影响 |
|------|------|------------|
| 严重 | 严重问题（严重 bug、安全漏洞） | 阻止提交 |
| 一般 | 警告（不规范但不一定错误） | 不阻止，建议修复 |
| 轻微 | 轻微问题（代码风格、建议优化） | 不阻止，可后续修复 |

### 文本报告 (txt)

- Markdown 表格格式，适合在终端或编辑器直接查看
- 五列结构清晰易读
- 包含统计汇总
- 优先级使用颜色标识

### HTML 报告 (html)

- Bootstrap 样式的响应式表格
- 不同优先级使用不同颜色标识
- 包含语法高亮的代码片段
- 便于分享和查看

### JSON 报告 (json)

- 结构化的 JSON 格式
- 包含所有审查信息的详细数据
- 适合与其他工具集成（如 CI/CD 系统）
- 便于自动化处理和分析
```

- [ ] **Step 2: 提交**
```bash
git add README.md
git commit -m "docs:更新README.md说明文档"
```

---

## 执行方式

**计划已完成并保存到** `docs/superpowers/plans/2026-03-27-unified-report-format-implementation.md`。

**两个执行选项：**

1. **Subagent-Driven (推荐)** - 我为每个任务分派独立的 subagent，任务间审查，快速迭代
2. **Inline Execution** - 在当前会话执行，批处理加检查点

**Which approach?**
