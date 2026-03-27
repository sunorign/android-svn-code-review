import json
from typing import List, Dict, Any

from src.local_rules.base_rule import RuleFinding
from src.ai_reviewer.base_client import AIReviewFinding
from .base_reporter import BaseReporter


class JSONReporter(BaseReporter):
    """生成代码审查结果的JSON格式报告。"""

    def _serialize_rule_finding(self, finding: RuleFinding) -> Dict[str, Any]:
        """将RuleFinding序列化为字典。"""
        return {
            "file_path": finding.file_path,
            "line_number": finding.line_number,
            "rule_name": finding.rule_name,
            "message": finding.message,
            "severity": finding.severity,
            "code_snippet": finding.code_snippet
        }

    def _serialize_ai_finding(self, finding: AIReviewFinding) -> Dict[str, Any]:
        """将AIReviewFinding序列化为字典。"""
        return {
            "file_path": finding.file_path,
            "line_start": finding.line_start,
            "line_end": finding.line_end,
            "issue_type": finding.issue_type,
            "severity": finding.severity,
            "message": finding.message,
            "suggestion": finding.suggestion
        }

    def generate_report(self,
                       local_findings: List[RuleFinding],
                       ai_findings: List[AIReviewFinding],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """生成JSON报告内容。"""
        report_data = {
            "meta": meta,
            "local_findings": [self._serialize_rule_finding(f) for f in local_findings],
            "ai_findings": [self._serialize_ai_finding(f) for f in ai_findings],
            "libs_reminder": libs_reminder
        }

        return json.dumps(report_data, ensure_ascii=False, indent=2, default=str)

    def _get_file_extension(self) -> str:
        """获取JSON报告的文件扩展名。"""
        return "json"
