package com.codereview.rules.common.java

import com.codereview.core.BaseRule
import com.codereview.core.FileDiff
import com.codereview.core.Finding
import com.codereview.core.DiffChange
import com.codereview.core.Severity

internal class JavaNpeRiskRule : BaseRule() {
    override val name: String get() = "Java-NPERisk"
    override val description: String get() = "识别可能的空指针异常风险"

    private val patterns = listOf(
        Regex("\\w+\\.\\w+\\(\\)"),
        Regex("\\w+\\.\\w+")
    )

    override fun checkDiff(fileDiff: FileDiff, change: DiffChange): List<Finding> {
        val findings = mutableListOf<Finding>()
        if (!change.isAdded) return findings

        val line = change.content
        // 简化版检测：查找方法调用链，如果变量名看起来可能为null且没有判空检查
        val hasNullCheck = line.contains(" == ") || line.contains(" != ") || line.contains("?.") || line.contains("if (")
        if (!hasNullCheck) {
            for (pattern in patterns) {
                for (match in pattern.findAll(line)) {
                    val matched = match.value
                    if (matched.count { it == '.' } >= 2 && !isLineComment(line)) {
                        findings.add(
                            Finding(
                                filePath = fileDiff.filePath,
                                lineNumber = change.lineNumber,
                                ruleName = name,
                                message = "多级调用可能存在空指针风险，建议增加判空检查",
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

    override fun checkFullFile(filePath: String, content: String): List<Finding> {
        val findings = mutableListOf<Finding>()
        val lines = content.lines()
        for ((index, line) in lines.withIndex()) {
            val lineNumber = index + 1
            val hasNullCheck = line.contains(" == ") || line.contains(" != ") || line.contains("?.") || line.contains("if (")
            if (!hasNullCheck) {
                for (pattern in patterns) {
                    for (match in pattern.findAll(line)) {
                        val matched = match.value
                        if (matched.count { it == '.' } >= 2 && !isLineComment(line)) {
                            findings.add(
                                Finding(
                                    filePath = filePath,
                                    lineNumber = lineNumber,
                                    ruleName = name,
                                    message = "多级调用可能存在空指针风险，建议增加判空检查",
                                    severity = Severity.WARNING,
                                    codeSnippet = line.trim()
                                )
                            )
                        }
                    }
                }
            }
        }
        return findings
    }
}