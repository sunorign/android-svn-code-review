import pytest
from src.reporter.unified_finding_processor import UnifiedFindingProcessor
from src.local_rules.base_rule import RuleFinding
from src.ai_reviewer.base_client import AIReviewFinding
from src.reporter.unified_finding import UnifiedFinding


def test_convert_rule_finding():
    """测试将 RuleFinding 转换为 UnifiedFinding。"""
    processor = UnifiedFindingProcessor()

    rule_finding = RuleFinding(
        file_path="MainActivity.java",
        line_number=100,
        rule_name="硬编码 URL 检查",
        message="发现硬编码的 URL: http://example.com",
        severity="BLOCK",
        code_snippet="String url = \"http://example.com\";"
    )

    unified_finding = processor.convert_rule_finding(rule_finding)

    assert isinstance(unified_finding, UnifiedFinding)
    assert unified_finding.priority == "严重"
    assert unified_finding.issue_type == "硬编码 URL 检查"
    assert unified_finding.location == "MainActivity.java:100"
    assert unified_finding.description == "发现硬编码的 URL: http://example.com"
    assert unified_finding.suggestion == ""


def test_convert_rule_finding_warning():
    """测试将 WARNING 级别的 RuleFinding 转换为 UnifiedFinding。"""
    processor = UnifiedFindingProcessor()

    rule_finding = RuleFinding(
        file_path="Utils.java",
        line_number=50,
        rule_name="调试日志检查",
        message="发现调试日志输出",
        severity="WARNING",
        code_snippet="Log.d(TAG, \"Debug message\");"
    )

    unified_finding = processor.convert_rule_finding(rule_finding)

    assert unified_finding.priority == "一般"


def test_convert_ai_finding():
    """测试将 AIReviewFinding 转换为 UnifiedFinding。"""
    processor = UnifiedFindingProcessor()

    ai_finding = AIReviewFinding(
        file_path="ApiClient.java",
        line_start=80,
        line_end=90,
        issue_type="性能问题",
        severity="阻断",
        message="网络请求超时设置过短，可能导致不稳定",
        suggestion="建议将超时时间从 5 秒增加到 30 秒"
    )

    unified_finding = processor.convert_ai_finding(ai_finding)

    assert isinstance(unified_finding, UnifiedFinding)
    assert unified_finding.priority == "严重"
    assert unified_finding.issue_type == "性能问题"
    assert unified_finding.location == "ApiClient.java:80-90"
    assert unified_finding.description == "网络请求超时设置过短，可能导致不稳定"
    assert unified_finding.suggestion == "建议将超时时间从 5 秒增加到 30 秒"


def test_convert_ai_finding_warning():
    """测试将 WARNING 级别的 AIReviewFinding 转换为 UnifiedFinding。"""
    processor = UnifiedFindingProcessor()

    ai_finding = AIReviewFinding(
        file_path="UserService.java",
        line_start=20,
        line_end=25,
        issue_type="代码风格",
        severity="警告",
        message="变量名不符合驼峰命名规范",
        suggestion="建议将变量名改为 camelCase 格式"
    )

    unified_finding = processor.convert_ai_finding(ai_finding)

    assert unified_finding.priority == "一般"


def test_process_all_findings():
    """测试处理所有类型的发现。"""
    processor = UnifiedFindingProcessor()

    rule_finding = RuleFinding(
        file_path="MainActivity.java",
        line_number=100,
        rule_name="硬编码 URL 检查",
        message="发现硬编码的 URL",
        severity="BLOCK"
    )

    ai_finding = AIReviewFinding(
        file_path="ApiClient.java",
        line_start=80,
        line_end=90,
        issue_type="性能问题",
        severity="阻断",
        message="网络请求超时设置过短"
    )

    unified_finding = UnifiedFinding(
        priority="严重",
        issue_type="内存泄漏",
        location="MainActivity.java:120",
        description="Handler 持有外部类引用",
        suggestion="使用静态内部类 + WeakReference"
    )

    local_findings = [rule_finding, unified_finding]
    ai_findings = [ai_finding]
    converted = processor.process_all(local_findings, ai_findings)

    assert len(converted) == 3
    for finding in converted:
        assert isinstance(finding, UnifiedFinding)


def test_group_by_priority():
    """测试按优先级分组发现。"""
    processor = UnifiedFindingProcessor()

    findings = [
        UnifiedFinding(priority="严重", issue_type="问题1", location="file1:10", description="描述1", suggestion="建议1"),
        UnifiedFinding(priority="一般", issue_type="问题2", location="file2:20", description="描述2", suggestion="建议2"),
        UnifiedFinding(priority="严重", issue_type="问题3", location="file3:30", description="描述3", suggestion="建议3")
    ]

    grouped = processor.group_by_priority(findings)

    assert len(grouped["严重"]) == 2
    assert len(grouped["一般"]) == 1
    assert all(f.priority == "严重" for f in grouped["严重"])
    assert all(f.priority == "一般" for f in grouped["一般"])


def test_group_by_issue_type():
    """测试按问题类型分组发现。"""
    processor = UnifiedFindingProcessor()

    findings = [
        UnifiedFinding(priority="严重", issue_type="内存泄漏", location="file1:10", description="描述1", suggestion="建议1"),
        UnifiedFinding(priority="一般", issue_type="性能问题", location="file2:20", description="描述2", suggestion="建议2"),
        UnifiedFinding(priority="严重", issue_type="内存泄漏", location="file3:30", description="描述3", suggestion="建议3")
    ]

    grouped = processor.group_by_issue_type(findings)

    assert len(grouped["内存泄漏"]) == 2
    assert len(grouped["性能问题"]) == 1
    assert all(f.issue_type == "内存泄漏" for f in grouped["内存泄漏"])
    assert all(f.issue_type == "性能问题" for f in grouped["性能问题"])


def test_empty_findings():
    """测试转换空发现列表。"""
    processor = UnifiedFindingProcessor()

    converted = processor.process_all([], [])
    assert len(converted) == 0

    grouped_priority = processor.group_by_priority([])
    assert len(grouped_priority["严重"]) == 0
    assert len(grouped_priority["一般"]) == 0

    grouped_type = processor.group_by_issue_type([])
    assert len(grouped_type) == 0
