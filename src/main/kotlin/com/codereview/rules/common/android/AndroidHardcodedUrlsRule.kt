package com.codereview.rules.common.android

import com.codereview.core.BaseRule
import com.codereview.core.FileDiff
import com.codereview.core.Finding
import com.codereview.core.DiffChange
import com.codereview.core.Severity
import com.codereview.core.RuleGroup

internal class AndroidHardcodedUrlsRule : BaseRule() {
    override val name: String get() = "Android-HardcodedUrls"
    override val description: String get() = "检查硬编码的IP地址或URL"
    override val group: RuleGroup get() = RuleGroup.ANDROID_COMMON

    private val patterns = listOf(
        Regex("http://\\d+\\.\\d+\\.\\d+\\.\\d+"),
        Regex("https://\\d+\\.\\d+\\.\\d+\\.\\d+"),
        Regex("http://[^/]+\\.([^\\s\"]+)"),
        Regex("\"http://"),
        Regex("\"https://")
    )

    override fun checkDiff(fileDiff: FileDiff, change: DiffChange): List<Finding> {
        val findings = mutableListOf<Finding>()
        if (!change.isAdded) return findings

        val line = change.content
        // 排除注释和字符串资源文件引用
        if (line.contains("@string/")) return findings

        for (pattern in patterns) {
            for (match in pattern.findAll(line)) {
                if (!isLineComment(line) && !isPatternInString(line, match.range.first, match.range.last)) {
                    findings.add(
                        Finding(
                            filePath = fileDiff.filePath,
                            lineNumber = change.lineNumber,
                            ruleName = name,
                            message = "发现硬编码URL/IP，应该配置在 gradle 或 resources 中",
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
            if (line.contains("@string/")) continue
            val lineNumber = index + 1
            for (pattern in patterns) {
                for (match in pattern.findAll(line)) {
                    if (!isLineComment(line) && !isPatternInString(line, match.range.first, match.range.last)) {
                        findings.add(
                            Finding(
                                filePath = filePath,
                                lineNumber = lineNumber,
                                ruleName = name,
                                message = "发现硬编码URL/IP，应该配置在 gradle 或 resources 中",
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