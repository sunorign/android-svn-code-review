package com.codereview.rules.common.java

import com.codereview.core.BaseRule
import com.codereview.core.FileDiff
import com.codereview.core.Finding
import com.codereview.core.DiffChange
import com.codereview.core.Severity
import com.codereview.core.RuleGroup

internal class JavaDebugLoggingRule : BaseRule() {
    override val name: String get() = "Java-DebugLogging"
    override val description: String get() = "检查调试日志代码(System.out.println/Log.d)"
    override val group: RuleGroup get() = RuleGroup.JAVA_COMMON

    private val patterns = listOf(
        Regex("System\\.out\\.println"),
        Regex("Log\\.d\\s*\\("),
        Regex("Log\\.v\\s*\\(")
    )

    override fun checkDiff(fileDiff: FileDiff, change: DiffChange): List<Finding> {
        val findings = mutableListOf<Finding>()
        if (!change.isAdded) return findings

        val line = change.content
        for (pattern in patterns) {
            for (match in pattern.findAll(line)) {
                if (!isLineComment(line) && !isPatternInString(line, match.range.first, match.range.last)) {
                    findings.add(
                        Finding(
                            filePath = fileDiff.filePath,
                            lineNumber = change.lineNumber,
                            ruleName = name,
                            message = "发现调试日志代码，发布前应该移除",
                            severity = Severity.BLOCK,
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
            for (pattern in patterns) {
                for (match in pattern.findAll(line)) {
                    if (!isLineComment(line) && !isPatternInString(line, match.range.first, match.range.last)) {
                        findings.add(
                            Finding(
                                filePath = filePath,
                                lineNumber = lineNumber,
                                ruleName = name,
                                message = "发现调试日志代码，发布前应该移除",
                                severity = Severity.BLOCK,
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