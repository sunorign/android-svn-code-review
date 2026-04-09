package com.codereview.rules.common.android

import com.codereview.core.BaseRule
import com.codereview.core.FileDiff
import com.codereview.core.Finding
import com.codereview.core.DiffChange
import com.codereview.core.Severity
import com.codereview.core.RuleGroup

internal class AndroidViewHolderPatternRule : BaseRule() {
    override val name: String get() = "Android-ViewHolderPattern"
    override val description: String get() = "检查 ViewHolder 模式的正确使用"
    override val group: RuleGroup get() = RuleGroup.ANDROID_COMMON

    override fun checkDiff(fileDiff: FileDiff, change: DiffChange): List<Finding> {
        val findings = mutableListOf<Finding>()
        if (!change.isAdded) return findings
        if (!fileDiff.filePath.contains("Adapter", ignoreCase = true)) return findings

        val line = change.content
        if (line.contains("findViewById") && !isLineComment(line)) {
            findings.add(
                Finding(
                    filePath = fileDiff.filePath,
                    lineNumber = change.lineNumber,
                    ruleName = name,
                    message = "在Adapter中应该使用ViewHolder模式，避免每次都调用findViewById",
                    severity = Severity.WARNING,
                    codeSnippet = line.trim()
                )
            )
        }
        return findings
    }

    override fun checkFullFile(filePath: String, content: String): List<Finding> {
        val findings = mutableListOf<Finding>()
        if (!filePath.contains("Adapter", ignoreCase = true)) return findings

        val lines = content.lines()
        val hasViewHolder = content.contains("ViewHolder")
        if (!hasViewHolder) {
            for ((index, line) in lines.withIndex()) {
                val lineNumber = index + 1
                if (line.contains("findViewById") && !isLineComment(line)) {
                    findings.add(
                        Finding(
                            filePath = filePath,
                            lineNumber = lineNumber,
                            ruleName = name,
                            message = "在Adapter中应该使用ViewHolder模式，避免每次都调用findViewById",
                            severity = Severity.WARNING,
                            codeSnippet = line.trim()
                        )
                    )
                }
            }
        }
        return findings
    }
}