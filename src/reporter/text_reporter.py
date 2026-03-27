import datetime
from typing import List, Dict, Any
from collections import defaultdict

from src.local_rules.base_rule import RuleFinding
from src.ai_reviewer.base_client import AIReviewFinding
from .base_reporter import BaseReporter


class TextReporter(BaseReporter):
    """Generate plain text format report for code review results."""

    def generate_report(self,
                       local_findings: List[RuleFinding],
                       ai_findings: List[AIReviewFinding],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """Generate text report content."""
        timestamp = meta.get('timestamp', datetime.datetime.now().isoformat())
        mode = meta.get('mode', 'unknown')
        file_count = meta.get('file_count', 0)
        has_blocking = meta.get('has_blocking', False)
        libs_change = meta.get('libs_change', False)

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

        # Group findings by file
        local_by_file = defaultdict(list)
        for finding in local_findings:
            local_by_file[finding.file_path].append(finding)

        ai_by_file = defaultdict(list)
        for finding in ai_findings:
            ai_by_file[finding.file_path].append(finding)

        # Local findings section
        if local_findings:
            report.append(f"LOCAL RULE FINDINGS: {len(local_findings)} issues")
            report.append("-" * 80)

            for file_path, findings in local_by_file.items():
                report.append(f"\nFile: {file_path}")
                report.append(f"  Found {len(findings)} issues:")

                for i, finding in enumerate(findings, 1):
                    severity_tag = f"[BLOCK]" if finding.severity.upper() == "BLOCK" else "[WARNING]"
                    report.append(f"    {i}. {severity_tag} {finding.rule_name}")
                    report.append(f"       Line {finding.line_number}: {finding.message}")

                    if finding.code_snippet:
                        report.append(f"       Code snippet:")
                        for line in finding.code_snippet.split('\n'):
                            report.append(f"         {line}")
            report.append("")

        # AI findings section
        if ai_findings:
            report.append(f"AI REVIEW FINDINGS: {len(ai_findings)} issues")
            report.append("-" * 80)

            for file_path, findings in ai_by_file.items():
                report.append(f"\nFile: {file_path}")
                report.append(f"  Found {len(findings)} issues:")

                for i, finding in enumerate(findings, 1):
                    severity_tag = f"[BLOCK]" if finding.severity.upper() == "BLOCK" else "[WARNING]"
                    report.append(f"    {i}. {severity_tag} {finding.issue_type}")
                    report.append(f"       Lines {finding.line_start}-{finding.line_end}: {finding.message}")

                    if finding.suggestion:
                        report.append(f"       Suggestion: {finding.suggestion}")
            report.append("")

        # Summary
        total_issues = len(local_findings) + len(ai_findings)
        report.append(f"\n{'=' * 80}")
        report.append(f"SUMMARY: Total issues found - {total_issues}")
        report.append(f"  - Local rules: {len(local_findings)}")
        report.append(f"  - AI review: {len(ai_findings)}")
        report.append(f"{'=' * 80}")

        return "\n".join(report)

    def _get_file_extension(self) -> str:
        """Get file extension for text report."""
        return "txt"
