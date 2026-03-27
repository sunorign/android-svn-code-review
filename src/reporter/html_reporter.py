import html
import re
import datetime
from typing import List, Dict, Any
from collections import defaultdict

from src.local_rules.base_rule import RuleFinding
from src.ai_reviewer.base_client import AIReviewFinding
from .base_reporter import BaseReporter


class HTMLReporter(BaseReporter):
    """生成代码审查结果的HTML格式报告。"""

    @staticmethod
    def _sanitize_html_id(text: str) -> str:
        """清理文本以用作HTML ID，将所有非字母数字字符替换为下划线。"""
        return re.sub(r'[^a-zA-Z0-9]', '_', text)

    def generate_report(self,
                       local_findings: List[RuleFinding],
                       ai_findings: List[AIReviewFinding],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """生成HTML报告内容。"""
        timestamp = meta.get('timestamp', datetime.datetime.now().isoformat())
        mode = meta.get('mode', 'unknown')
        file_count = meta.get('file_count', 0)
        has_blocking = meta.get('has_blocking', False)
        libs_change = meta.get('libs_change', False)

        output = []
        output.append("<!DOCTYPE html>")
        output.append("<html lang=\"en\">")
        output.append("<head>")
        output.append("    <meta charset=\"UTF-8\">")
        output.append("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
        output.append("    <title>Code Review Report</title>")
        output.append("    <style>")
        output.append("        * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }")
        output.append("        body { background-color: #f5f5f5; padding: 20px; }")
        output.append("        .report-container { max-width: 1200px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }")
        output.append("        h1 { color: #333; font-size: 28px; margin-bottom: 20px; border-bottom: 2px solid #ddd; padding-bottom: 10px; }")
        output.append("        .header-info { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; font-size: 14px; }")
        output.append("        .info-item { padding: 10px; background: #f9f9f9; border-radius: 5px; }")
        output.append("        .info-label { font-weight: bold; color: #666; margin-right: 5px; }")
        output.append("        .section { margin-bottom: 40px; }")
        output.append("        .section h2 { color: #333; font-size: 20px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #ddd; }")
        output.append("        .file-block { margin-bottom: 30px; }")
        output.append("        .file-header { background: #f0f0f0; padding: 12px; border-radius: 5px; cursor: pointer; }")
        output.append("        .file-header:hover { background: #e8e8e8; }")
        output.append("        .file-path { font-weight: bold; color: #333; font-size: 16px; }")
        output.append("        .file-count { color: #666; font-size: 14px; margin-left: 10px; }")
        output.append("        .file-content { padding: 15px; border-left: 3px solid #ddd; margin-top: 10px; display: none; }")
        output.append("        .file-content.active { display: block; }")
        output.append("        .finding-item { margin-bottom: 20px; padding: 15px; border-radius: 5px; }")
        output.append("        .finding-block { background: #ffebee; border-left: 5px solid #c62828; }")
        output.append("        .finding-warning { background: #fff3e0; border-left: 5px solid #ef6c00; }")
        output.append("        .finding-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }")
        output.append("        .finding-title { font-weight: bold; color: #333; font-size: 16px; }")
        output.append("        .finding-severity { font-size: 12px; padding: 3px 8px; border-radius: 3px; font-weight: bold; }")
        output.append("        .severity-block { background: #c62828; color: white; }")
        output.append("        .severity-warning { background: #ef6c00; color: white; }")
        output.append("        .finding-detail { margin-bottom: 10px; }")
        output.append("        .finding-line { color: #666; font-size: 14px; margin-bottom: 5px; }")
        output.append("        .finding-message { color: #333; font-size: 15px; line-height: 1.5; }")
        output.append("        .code-snippet { background: #f8f8f8; border: 1px solid #ddd; padding: 10px; margin-top: 10px; border-radius: 5px; overflow-x: auto; }")
        output.append("        .code-snippet pre { font-family: monospace; font-size: 13px; white-space: pre-wrap; line-height: 1.4; }")
        output.append("        .summary { background: #f9f9f9; padding: 20px; border-radius: 5px; margin-top: 40px; }")
        output.append("        .summary h3 { color: #333; font-size: 18px; margin-bottom: 15px; }")
        output.append("        .summary-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }")
        output.append("        .stat-item { padding: 10px; background: #fff; border-radius: 5px; }")
        output.append("        .stat-value { font-size: 20px; font-weight: bold; color: #333; }")
        output.append("    </style>")
        output.append("    <script>")
        output.append("        function toggleFileContent(filePath) {")
        output.append("            const content = document.getElementById(`file-content-${filePath}`);")
        output.append("            content.classList.toggle('active');")
        output.append("        }")
        output.append("    </script>")
        output.append("</head>")
        output.append("<body>")
        output.append("    <div class=\"report-container\">")
        output.append("        <h1>Code Review Report</h1>")

        output.append("        <div class=\"header-info\">")
        output.append(f"            <div class=\"info-item\"><span class=\"info-label\">Generated:</span>{html.escape(timestamp)}</div>")
        output.append(f"            <div class=\"info-item\"><span class=\"info-label\">Mode:</span>{html.escape(mode)}</div>")
        output.append(f"            <div class=\"info-item\"><span class=\"info-label\">Files processed:</span>{html.escape(str(file_count))}</div>")
        output.append(f"            <div class=\"info-item\"><span class=\"info-label\">Blocking issues:</span>{'YES' if has_blocking else 'NO'}</div>")
        output.append(f"            <div class=\"info-item\"><span class=\"info-label\">Library changes:</span>{'YES' if libs_change else 'NO'}</div>")
        if libs_reminder:
            output.append(f"            <div class=\"info-item\"><span class=\"info-label\">Library reminder:</span>{html.escape(libs_reminder)}</div>")
        output.append("        </div>")

        # 本地审查结果部分
        if local_findings:
            output.append("        <div class=\"section\">")
            output.append(f"            <h2>Local Rule Findings: {len(local_findings)} issues</h2>")

            local_by_file = defaultdict(list)
            for finding in local_findings:
                local_by_file[finding.file_path].append(finding)

            for file_path, findings in local_by_file.items():
                sanitized_path = self._sanitize_html_id(file_path)
                output.append(f"            <div class=\"file-block\">")
                output.append(f"                <div class=\"file-header\" onclick=\"toggleFileContent('{sanitized_path}')\">")
                output.append(f"                    <span class=\"file-path\">{html.escape(file_path)}</span>")
                output.append(f"                    <span class=\"file-count\">{len(findings)} issues</span>")
                output.append(f"                </div>")
                output.append(f"                <div class=\"file-content\" id=\"file-content-{sanitized_path}\">")

                for finding in findings:
                    severity_class = "finding-block" if finding.severity.upper() == "BLOCK" else "finding-warning"
                    severity_tag = "BLOCK" if finding.severity.upper() == "BLOCK" else "WARNING"
                    severity_style = "severity-block" if finding.severity.upper() == "BLOCK" else "severity-warning"

                    output.append(f"                    <div class=\"finding-item {severity_class}\">")
                    output.append(f"                        <div class=\"finding-header\">")
                    output.append(f"                            <div class=\"finding-title\">{html.escape(finding.rule_name)}</div>")
                    output.append(f"                            <div class=\"finding-severity {severity_style}\">{severity_tag}</div>")
                    output.append(f"                        </div>")
                    output.append(f"                        <div class=\"finding-detail\">")
                    output.append(f"                            <div class=\"finding-line\">Line {finding.line_number}</div>")
                    output.append(f"                            <div class=\"finding-message\">{html.escape(finding.message)}</div>")

                    if finding.code_snippet:
                        output.append(f"                            <div class=\"code-snippet\"><pre>{html.escape(finding.code_snippet)}</pre></div>")
                    output.append(f"                        </div>")
                    output.append(f"                    </div>")

                output.append(f"                </div>")
                output.append(f"            </div>")
            output.append("        </div>")

        # AI审查结果部分
        if ai_findings:
            output.append("        <div class=\"section\">")
            output.append(f"            <h2>AI Review Findings: {len(ai_findings)} issues</h2>")

            ai_by_file = defaultdict(list)
            for finding in ai_findings:
                ai_by_file[finding.file_path].append(finding)

            for file_path, findings in ai_by_file.items():
                sanitized_path = self._sanitize_html_id(f"{file_path}_ai")
                output.append(f"            <div class=\"file-block\">")
                output.append(f"                <div class=\"file-header\" onclick=\"toggleFileContent('{sanitized_path}')\">")
                output.append(f"                    <span class=\"file-path\">{html.escape(file_path)}</span>")
                output.append(f"                    <span class=\"file-count\">{len(findings)} issues</span>")
                output.append(f"                </div>")
                output.append(f"                <div class=\"file-content\" id=\"file-content-{sanitized_path}\">")

                for finding in findings:
                    severity_class = "finding-block" if finding.severity.upper() == "BLOCK" else "finding-warning"
                    severity_tag = "BLOCK" if finding.severity.upper() == "BLOCK" else "WARNING"
                    severity_style = "severity-block" if finding.severity.upper() == "BLOCK" else "severity-warning"

                    output.append(f"                    <div class=\"finding-item {severity_class}\">")
                    output.append(f"                        <div class=\"finding-header\">")
                    output.append(f"                            <div class=\"finding-title\">{html.escape(finding.issue_type)}</div>")
                    output.append(f"                            <div class=\"finding-severity {severity_style}\">{severity_tag}</div>")
                    output.append(f"                        </div>")
                    output.append(f"                        <div class=\"finding-detail\">")
                    output.append(f"                            <div class=\"finding-line\">Lines {finding.line_start}-{finding.line_end}</div>")
                    output.append(f"                            <div class=\"finding-message\">{html.escape(finding.message)}</div>")

                    if finding.suggestion:
                        output.append(f"                            <div class=\"finding-message\">Suggestion: {html.escape(finding.suggestion)}</div>")
                    output.append(f"                        </div>")
                    output.append(f"                    </div>")

                output.append(f"                </div>")
                output.append(f"            </div>")
            output.append("        </div>")

        # 总结部分
        output.append("        <div class=\"summary\">")
        output.append("            <h3>Summary</h3>")
        output.append("            <div class=\"summary-stats\">")
        output.append(f"                <div class=\"stat-item\">")
        output.append(f"                    <div class=\"info-label\">Total issues:</div>")
        output.append(f"                    <div class=\"stat-value\">{len(local_findings) + len(ai_findings)}</div>")
        output.append(f"                </div>")
        output.append(f"                <div class=\"stat-item\">")
        output.append(f"                    <div class=\"info-label\">Local issues:</div>")
        output.append(f"                    <div class=\"stat-value\">{len(local_findings)}</div>")
        output.append(f"                </div>")
        output.append(f"                <div class=\"stat-item\">")
        output.append(f"                    <div class=\"info-label\">AI issues:</div>")
        output.append(f"                    <div class=\"stat-value\">{len(ai_findings)}</div>")
        output.append(f"                </div>")
        output.append("            </div>")
        output.append("        </div>")

        output.append("    </div>")
        output.append("</body>")
        output.append("</html>")

        return "\n".join(output)

    def _get_file_extension(self) -> str:
        """获取HTML报告的文件扩展名。"""
        return "html"
