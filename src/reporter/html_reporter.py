import datetime
from typing import List, Dict, Any
from src.reporter.unified_finding import UnifiedFinding
from .base_reporter import BaseReporter


class HTMLReporter(BaseReporter):
    """生成代码审查结果的 HTML 格式报告。"""

    def generate_report(self,
                       findings: List[UnifiedFinding],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """生成 HTML 报告内容。"""
        timestamp = meta.get('timestamp', datetime.datetime.now().isoformat())
        mode = meta.get('mode', 'unknown')
        file_count = meta.get('file_count', 0)
        has_blocking = any(finding.priority == "严重" for finding in findings)
        libs_change = meta.get('libs_change', False)

        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang=\"zh-CN\">")
        html.append("<head>")
        html.append("    <meta charset=\"UTF-8\">")
        html.append("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
        html.append("    <title>代码审查报告</title>")
        html.append("    <link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css\">")
        html.append("    <style>")
        html.append("        body { font-family: 'Segoe UI', sans-serif; margin: 20px; }")
        html.append("        .report-header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }")
        html.append("        .report-header h1 { color: #333; font-size: 24px; margin: 0; }")
        html.append("        .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 14px; }")
        html.append("        .severity-high { background-color: #dc3545; color: white; }")
        html.append("        .severity-medium { background-color: #ffc107; color: black; }")
        html.append("        .severity-low { background-color: #17a2b8; color: white; }")
        html.append("    </style>")
        html.append("</head>")
        html.append("<body>")
        html.append("<div class=\"container\">")

        # 报告头部
        html.append("<div class=\"report-header\">")
        html.append("    <h1>代码审查报告</h1>")
        html.append("    <div style=\"margin-top: 10px;\">")
        html.append(f"        <p style=\"margin: 5px 0;\">生成时间: {timestamp}</p>")
        html.append(f"        <p style=\"margin: 5px 0;\">模式: {mode}</p>")
        html.append(f"        <p style=\"margin: 5px 0;\">处理文件数: {file_count}</p>")
        html.append(f"        <p style=\"margin: 5px 0;\">阻塞问题: {'<span class=\"status-badge severity-high\">严重</span>' if has_blocking else '无'}</p>")
        html.append(f"        <p style=\"margin: 5px 0;\">库变更: {'有' if libs_change else '无'}</p>")
        if libs_reminder:
            html.append(f"        <p style=\"margin: 5px 0;\">库提醒: {libs_reminder}</p>")
        html.append("    </div>")
        html.append("</div>")

        # 表格内容
        if findings:
            html.append(f"<h2>发现的问题 ({len(findings)} 个)</h2>")
            html.append("<div class=\"table-responsive\">")
            html.append("<table class=\"table table-bordered table-hover\">")
            html.append("    <thead class=\"thead-light\">")
            html.append("        <tr>")
            html.append("            <th>优先级</th>")
            html.append("            <th>问题类型</th>")
            html.append("            <th>位置</th>")
            html.append("            <th>说明</th>")
            html.append("            <th>修复建议</th>")
            html.append("        </tr>")
            html.append("    </thead>")
            html.append("    <tbody>")

            for finding in findings:
                severity_class = {
                    "严重": "danger",
                    "一般": "warning",
                    "轻微": "info"
                }[finding.priority]

                badge_class = {
                    "严重": "severity-high",
                    "一般": "severity-medium",
                    "轻微": "severity-low"
                }[finding.priority]

                html.append("        <tr class=\"table-" + severity_class + "\">")
                html.append(f"            <td><span class=\"status-badge {badge_class}\">{finding.priority}</span></td>")
                html.append(f"            <td>{finding.issue_type}</td>")
                html.append(f"            <td>{finding.location}</td>")
                html.append(f"            <td>{finding.description}</td>")
                html.append(f"            <td>{finding.suggestion if finding.suggestion else '-'}</td>")
                html.append("        </tr>")

            html.append("    </tbody>")
            html.append("</table>")
            html.append("</div>")
        else:
            html.append("<div class=\"alert alert-success\">")
            html.append("    <h4 class=\"alert-heading\">审查通过！</h4>")
            html.append("    <p>未发现需要处理的问题。</p>")
            html.append("</div>")

        # 总结
        html.append("<div style=\"margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;\">")
        html.append("<h3>问题统计</h3>")
        html.append(f"<p>严重: {sum(1 for f in findings if f.priority == '严重')}</p>")
        html.append(f"<p>一般: {sum(1 for f in findings if f.priority == '一般')}</p>")
        html.append(f"<p>轻微: {sum(1 for f in findings if f.priority == '轻微')}</p>")
        html.append("</div>")

        html.append("</div>")
        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def _get_file_extension(self) -> str:
        """获取 HTML 报告的文件扩展名。"""
        return "html"
