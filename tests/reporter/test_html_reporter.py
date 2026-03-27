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


def test_html_reporter_multiple_findings():
    reporter = HTMLReporter()
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
        ),
        UnifiedFinding(
            priority="轻微",
            issue_type="代码风格",
            location="Utils.java:42",
            description="未使用 try-with-resources",
            suggestion="改用 try-with-resources 语法"
        )
    ]

    report = reporter.generate_report(findings, {})

    assert "内存泄露" in report
    assert "超时处理不足" in report
    assert "代码风格" in report
    assert "table-danger" in report
    assert "table-warning" in report
    assert "table-info" in report


def test_html_reporter_no_findings():
    reporter = HTMLReporter()
    report = reporter.generate_report([], {})

    assert "审查通过" in report
    assert "未发现需要处理的问题" in report


def test_html_reporter_statistics():
    reporter = HTMLReporter()
    findings = [
        UnifiedFinding(priority="严重", issue_type="a", location="", description="", suggestion=""),
        UnifiedFinding(priority="一般", issue_type="b", location="", description="", suggestion=""),
        UnifiedFinding(priority="一般", issue_type="c", location="", description="", suggestion=""),
        UnifiedFinding(priority="轻微", issue_type="d", location="", description="", suggestion="")
    ]

    report = reporter.generate_report(findings, {})

    assert "严重: 1" in report
    assert "一般: 2" in report
    assert "轻微: 1" in report


def test_html_reporter_metadata():
    reporter = HTMLReporter()
    meta = {
        "timestamp": "2026-03-27T10:30:00",
        "mode": "diff-review",
        "file_count": 5,
        "libs_change": True
    }

    report = reporter.generate_report([], meta)

    assert "2026-03-27T10:30:00" in report
    assert "diff-review" in report
    assert "处理文件数: 5" in report
    assert "库变更: 有" in report


def test_html_reporter_libs_reminder():
    reporter = HTMLReporter()
    report = reporter.generate_report([], {}, "请注意更新第三方库")

    assert "库提醒: 请注意更新第三方库" in report


def test_html_reporter_empty_suggestion():
    reporter = HTMLReporter()
    findings = [
        UnifiedFinding(
            priority="一般",
            issue_type="代码风格",
            location="Test.java:10",
            description="格式不规范",
            suggestion=""
        )
    ]

    report = reporter.generate_report(findings, {})

    assert "<td>-</td>" in report
