import pytest
from src.reporter.base_reporter import BaseReporter
from src.reporter.html_reporter import HTMLReporter
from src.reporter.json_reporter import JSONReporter
from src.reporter.text_reporter import TextReporter
from src.reporter.unified_finding import UnifiedFinding


class ConcreteReporter(BaseReporter):
    """用于测试BaseReporter的具体实现类"""
    def generate_report(self, findings, meta, libs_reminder=""):
        return "Test Report"

    def _get_file_extension(self):
        return "txt"


def test_base_reporter_initialization():
    reporter = ConcreteReporter()
    assert reporter is not None


def test_base_reporter_generation():
    reporter = ConcreteReporter()
    report = reporter.generate([], [], {})
    assert report is not None
    assert isinstance(report, str)


def test_all_reporters_inherit_from_base():
    assert issubclass(HTMLReporter, BaseReporter)
    assert issubclass(JSONReporter, BaseReporter)
    assert issubclass(TextReporter, BaseReporter)


def test_html_reporter_generate_method():
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
    assert report is not None
    assert isinstance(report, str)
    assert "内存泄露" in report


def test_json_reporter_generate_method():
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
    assert report is not None
    assert isinstance(report, str)
    assert "内存泄露" in report


def test_text_reporter_generate_method():
    reporter = TextReporter()
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
    assert report is not None
    assert isinstance(report, str)
    assert "内存泄露" in report


def test_generate_with_no_findings():
    reporter = ConcreteReporter()
    report = reporter.generate([], [], {})
    assert report is not None


def test_write_report_creates_file(tmp_path):
    import os
    output_dir = tmp_path / "reports"
    reporter = ConcreteReporter(output_dir=str(output_dir))

    # 应该创建目录
    assert os.path.exists(output_dir) is True

    # 生成报告
    report_path = reporter.generate([], [], {})

    assert report_path is not None
    assert os.path.exists(report_path) is True
    assert os.path.dirname(report_path) == str(output_dir)
