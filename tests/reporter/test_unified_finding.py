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
