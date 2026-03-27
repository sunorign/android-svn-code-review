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


def test_text_reporter_summary():
    reporter = TextReporter()
    findings = [
        UnifiedFinding(priority="严重", issue_type="a", location="", description="", suggestion=""),
        UnifiedFinding(priority="一般", issue_type="b", location="", description="", suggestion=""),
        UnifiedFinding(priority="一般", issue_type="c", location="", description="", suggestion=""),
        UnifiedFinding(priority="轻微", issue_type="d", location="", description="", suggestion="")
    ]

    report = reporter.generate_report(findings, {})

    assert "SUMMARY: Total issues found - 4" in report
    assert "严重: 1" in report
    assert "一般: 2" in report
    assert "轻微: 1" in report
