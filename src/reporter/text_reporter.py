import datetime
from typing import List, Dict, Any
from src.reporter.unified_finding import UnifiedFinding
from src.reporter.unified_finding_processor import UnifiedFindingProcessor
from .base_reporter import BaseReporter


class TextReporter(BaseReporter):
    """生成代码审查结果的 Markdown 表格格式文本报告。"""

    def __init__(self):
        super().__init__()
        self.processor = UnifiedFindingProcessor()

    def generate_report(self,
                       local_findings: List[Any],
                       ai_findings: List[Any],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """生成 Markdown 格式报告内容。"""
        timestamp = meta.get('timestamp', datetime.datetime.now().isoformat())
        mode = meta.get('mode', 'unknown')
        file_count = meta.get('file_count', 0)
        libs_change = meta.get('libs_change', False)

        # 处理所有发现为统一格式
        all_findings = local_findings + ai_findings
        findings = self.processor.process_all(all_findings)
        has_blocking = any(finding.priority == "严重" for finding in findings)

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
