import json
import datetime
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
