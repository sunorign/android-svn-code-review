package com.codereview.rules.common.java

import com.codereview.core.BaseRule
import com.codereview.core.FileDiff
import com.codereview.core.Finding
import com.codereview.core.DiffChange
import com.codereview.core.Severity
import com.codereview.core.RuleGroup

internal class JavaHardcodedSecretsRule : BaseRule() {
    override val name: String get() = "Java-HardcodedSecrets"
    override val description: String get() = "检测硬编码的密码、密钥、API Key等敏感信息"
    override val group: RuleGroup get() = RuleGroup.JAVA_COMMON

    private val patterns = listOf(
        Regex("password\\s*=\\s*[\"'][^\"']+[\"']", RegexOption.IGNORE_CASE),
        Regex("secret\\s*=\\s*[\"'][^\"']+[\"']", RegexOption.IGNORE_CASE),
        Regex("key\\s*=\\s*[\"'][A-Za-z0-9]{32,}[\"']", RegexOption.IGNORE_CASE),
        Regex("api[_-]key\\s*=\\s*[\"'][^\"']+[\"']", RegexOption.IGNORE_CASE),
        Regex("token\\s*=\\s*[\"'][^\"']+[\"']", RegexOption.IGNORE_CASE)
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
                            message = "发现硬编码敏感信息，应该从配置文件或环境变量读取",
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
                                message = "发现硬编码敏感信息，应该从配置文件或环境变量读取",
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