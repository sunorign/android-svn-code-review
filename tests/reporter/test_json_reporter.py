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
    assert '"total": 4' in report


def test_json_reporter_metadata():
    reporter = JSONReporter()
    meta = {
        "timestamp": "2026-03-27T10:30:00",
        "mode": "diff-review",
        "file_count": 5,
        "libs_change": True
    }

    report = reporter.generate_report([], meta)

    assert '"2026-03-27T10:30:00"' in report
    assert '"diff-review"' in report
    assert '"file_count": 5' in report
    assert '"libs_change": true' in report


def test_json_reporter_no_findings():
    reporter = JSONReporter()
    report = reporter.generate_report([], {})

    assert '"total": 0' in report


def test_json_reporter_libs_reminder():
    reporter = JSONReporter()
    report = reporter.generate_report([], {}, "请注意更新第三方库")

    assert '"libs_reminder": "请注意更新第三方库"' in report
