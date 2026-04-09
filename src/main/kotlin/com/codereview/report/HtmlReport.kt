package com.codereview.report

import com.codereview.core.Finding
import com.codereview.ai.AiFinding
import com.codereview.core.Severity
import java.io.File

internal class HtmlReport : ReportGenerator {
    override val extension: String get() = "html"

    override fun generate(result: ReviewResult, outputFile: File) {
        val html = buildString {
            append("""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Code Review 报告</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container mt-4">
<h1>Code Review 报告</h1>
<hr>
<div class="card mb-4">
<div class="card-body">
<p><strong>项目:</strong> ${result.projectName}</p>
<p><strong>扫描文件:</strong> ${result.scannedFiles}</p>
<p><strong>耗时:</strong> ${result.durationMs / 1000} 秒</p>
<p><strong>本地规则审查:</strong> ${if (result.localEnabled) "已启用" else "已禁用"}</p>
<p><strong>AI 辅助审查:</strong> ${if (result.aiEnabled) "已启用" else "已禁用"}</p>
""")

            // Always add link to log file - .log is always generated before html
            val logFileName = outputFile.name.replace(".html", ".log")
            append("""<p><strong>完整日志:</strong> <a href="${logFileName.htmlEscape()}">${logFileName.htmlEscape()}</a></p>
""")

            append("""
</div>
</div>
""")

            // Always render table if we have findings OR any alwaysDisplay rule
            val hasLocalFindingsOrAlwaysDisplay = result.localFindings.isNotEmpty() || result.loadedRules.any { it.alwaysDisplay }

            if (hasLocalFindingsOrAlwaysDisplay) {
                append("""
<h2>本地规则检查发现</h2>
<table class="table table-striped">
<thead>
<tr>
<th>优先级</th>
<th>规则名称</th>
<th>位置</th>
<th>问题描述</th>
<th>代码片段</th>
</tr>
</thead>
<tbody>
                """.trimIndent())

                for (finding in result.localFindings) {
                    val severityClass = if (finding.severity == Severity.BLOCK) "table-danger" else "table-warning"
                    val severityText = if (finding.severity == Severity.BLOCK) "BLOCK" else "WARNING"
                    append("""
<tr class="$severityClass">
<td>$severityText</td>
<td>${finding.ruleName.htmlEscape()}</td>
<td><code>${finding.filePath.htmlEscape()}:${finding.lineNumber}</code></td>
<td>${finding.message.htmlEscape()}</td>
<td><code>${finding.codeSnippet.htmlEscape()}</code></td>
</tr>
                    """.trimIndent())
                }

                // Add placeholder rows for alwaysDisplay rules that have no findings
                val ruleNamesWithFindings = result.localFindings.map { it.ruleName }.toSet()
                result.loadedRules.forEach { rule ->
                    if (rule.alwaysDisplay && !ruleNamesWithFindings.contains(rule.name)) {
                        append("""
<tr class="table-success">
<td>PASS</td>
<td>${rule.name.htmlEscape()}</td>
<td><code>-</code></td>
<td>未发现问题 ✓</td>
<td><code>-</code></td>
</tr>
                        """.trimIndent())
                    }
                }

                append("""
</tbody>
</table>
                """.trimIndent())
            }

            // Show AI error if AI is enabled and has error
            if (result.aiEnabled && result.aiErrorMessage != null) {
                append("""
<h2>AI 辅助审查</h2>
<div class="alert alert-danger" role="alert">
  <strong>AI 审查失败:</strong> ${result.aiErrorMessage.htmlEscape()}
</div>
                """.trimIndent())
            }

            if (result.aiFindings.isNotEmpty()) {
                append("""
<h2>AI 辅助审查发现</h2>
<div class="alert alert-info mb-3" role="alert">
  <strong>解析统计:</strong> AI 报告预期 ${result.aiExpectedTotal ?: "未知"} 个问题，实际解析出 ${result.aiFindings.size} 个
</div>
<table class="table table-striped">
<thead>
<tr>
<th>优先级</th>
<th>问题类型</th>
<th>位置</th>
<th>说明</th>
<th>修复建议</th>
<th>规则</th>
</tr>
</thead>
<tbody>
                """.trimIndent())

                for (finding in result.aiFindings) {
                    val severityClass = when (finding.priority.uppercase()) {
                        "BLOCK" -> "table-danger"
                        "WARNING" -> "table-warning"
                        else -> "table-info"
                    }
                    val displayPriority = when (finding.priority.uppercase()) {
                        "BLOCK" -> "BLOCK"
                        "WARNING" -> "WARNING"
                        else -> finding.priority
                    }
                    val ruleName = finding.metadata.ruleName
                    append("""
<tr class="$severityClass">
<td>$displayPriority</td>
<td>${finding.issueType.htmlEscape()}</td>
<td><code>${finding.location.htmlEscape()}</code></td>
<td>${finding.description.htmlEscape()}</td>
<td>${finding.suggestion.htmlEscape()}</td>
<td>${if (ruleName != null) ruleName.htmlEscape() else "-"}</td>
</tr>
                    """.trimIndent())
                }

                append("""
</tbody>
</table>
                """.trimIndent())
            }

            if (result.localFindings.isEmpty() && result.aiFindings.isEmpty()) {
                append("""
<div class="alert alert-success" role="alert">
<h4 class="alert-heading">检查完成</h4>
<p>未发现任何问题 ✅</p>
</div>
                """.trimIndent())
            }

            append("""
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
            """.trimIndent())
        }

        outputFile.writeText(html)
    }

    private fun String.htmlEscape(): String {
        return this.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&#039;")
    }
}
