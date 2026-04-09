package com.codereview.rules.common.java

import com.codereview.core.BaseRule
import com.codereview.core.FileDiff
import com.codereview.core.Finding
import com.codereview.core.DiffChange
import com.codereview.core.Severity
import com.codereview.core.RuleGroup

internal class JavaUnclosedResourcesRule : BaseRule() {
    override val name: String get() = "Java-UnclosedResources"
    override val description: String get() = "检查未关闭的资源(Cursor/Stream/Connection)"
    override val group: RuleGroup get() = RuleGroup.JAVA_COMMON

    private val resourceTypes = listOf(
        "Cursor", "Stream", "InputStream", "OutputStream", "Reader", "Writer",
        "Connection", "Statement", "PreparedStatement", "ResultSet",
        "FileInputStream", "FileOutputStream"
    )

    override fun checkDiff(fileDiff: FileDiff, change: DiffChange): List<Finding> {
        val findings = mutableListOf<Finding>()
        if (!change.isAdded) return findings

        val line = change.content
        for (type in resourceTypes) {
            if (line.contains("new $type") && !line.contains(".close()")) {
                if (!isLineComment(line)) {
                    findings.add(
                        Finding(
                            filePath = fileDiff.filePath,
                            lineNumber = change.lineNumber,
                            ruleName = name,
                            message = "资源创建后可能没有关闭，建议使用try-with-resources",
                            severity = Severity.WARNING,
                            codeSnippet = line.trim()
                        )
                    )
                }
            }
        }
        return findings
    }

    override fun checkFullFile(filePath: String, content: String): List<Finding> {
        val findings = mutableListOf<Finding>()
        val lines = content.lines()
        for ((index, line) in lines.withIndex()) {
            val lineNumber = index + 1
            for (type in resourceTypes) {
                if (line.contains("new $type") && !line.contains(".close()")) {
                    if (!isLineComment(line)) {
                        findings.add(
                            Finding(
                                filePath = filePath,
                                lineNumber = lineNumber,
                                ruleName = name,
                                message = "资源创建后可能没有关闭，建议使用try-with-resources",
                                severity = Severity.WARNING,
                                codeSnippet = line.trim()
                            )
                        )
                    }
                }
            }
        }
        return findings
    }
}