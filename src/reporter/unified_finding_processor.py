from typing import List, Any
from src.local_rules.base_rule import RuleFinding
from src.ai_reviewer.base_client import AIReviewFinding
from src.reporter.unified_finding import UnifiedFinding


class UnifiedFindingProcessor:
    """统一发现处理器，负责将不同格式的发现转换为统一格式。"""

    def __init__(self):
        """初始化统一发现处理器。"""
        pass

    def convert_rule_finding(self, finding: RuleFinding) -> UnifiedFinding:
        """将 RuleFinding 转换为 UnifiedFinding。"""
        # 转换严重程度
        priority = "严重" if finding.severity.upper() == "BLOCK" else "一般"
        location = f"{finding.file_path}:{finding.line_number}"
        return UnifiedFinding(
            priority=priority,
            issue_type=finding.rule_name,
            location=location,
            description=finding.message,
            suggestion=""
        )

    def convert_ai_finding(self, finding: AIReviewFinding) -> UnifiedFinding:
        """将 AIReviewFinding 转换为 UnifiedFinding。"""
        # 转换严重程度
        priority = "严重" if finding.severity.upper() == "阻断" else "一般"
        location = f"{finding.file_path}:{finding.line_start}-{finding.line_end}"
        return UnifiedFinding(
            priority=priority,
            issue_type=finding.issue_type,
            location=location,
            description=finding.message,
            suggestion=finding.suggestion or ""
        )

    def convert_all(self, findings: List[Any]) -> List[UnifiedFinding]:
        """将所有类型的发现转换为统一格式的列表。"""
        unified_findings = []

        for finding in findings:
            if isinstance(finding, RuleFinding):
                unified_findings.append(self.convert_rule_finding(finding))
            elif isinstance(finding, AIReviewFinding):
                unified_findings.append(self.convert_ai_finding(finding))
            elif isinstance(finding, UnifiedFinding):
                unified_findings.append(finding)

        return unified_findings

    def group_by_priority(self, findings: List[UnifiedFinding]) -> dict:
        """按优先级分组发现。"""
        grouped = {
            "严重": [],
            "一般": []
        }

        for finding in findings:
            if finding.priority in grouped:
                grouped[finding.priority].append(finding)
            else:
                grouped["一般"].append(finding)

        return grouped

    def group_by_issue_type(self, findings: List[UnifiedFinding]) -> dict:
        """按问题类型分组发现。"""
        grouped = {}

        for finding in findings:
            issue_type = finding.issue_type
            if issue_type not in grouped:
                grouped[issue_type] = []
            grouped[issue_type].append(finding)

        return grouped
