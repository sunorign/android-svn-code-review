package com.codereview.rules.common.android

import com.codereview.core.BaseRule
import com.codereview.core.FileDiff
import com.codereview.core.Finding
import com.codereview.core.DiffChange
import com.codereview.core.Severity

internal class AndroidBinaryFilesRule : BaseRule() {
    override val name: String get() = "Android-BinaryFiles"
    override val description: String get() = "阻止提交apk、dex等二进制文件"

    private val binaryExtensions = setOf(".apk", ".dex", ".aar", ".so")

    override fun checkDiff(fileDiff: FileDiff, change: DiffChange): List<Finding> {
        val findings = mutableListOf<Finding>()
        val filePathLower = fileDiff.filePath.lowercase()
        for (ext in binaryExtensions) {
            if (filePathLower.endsWith(ext)) {
                findings.add(
                    Finding(
                        filePath = fileDiff.filePath,
                        lineNumber = change.lineNumber,
                        ruleName = name,
                        message = "二进制文件不应该提交到版本控制",
                        severity = Severity.BLOCK,
                        codeSnippet = fileDiff.filePath
                    )
                )
            }
        }
        return findings
    }

    override fun checkFullFile(filePath: String, content: String): List<Finding> {
        val findings = mutableListOf<Finding>()
        val filePathLower = filePath.lowercase()
        for (ext in binaryExtensions) {
            if (filePathLower.endsWith(ext)) {
                findings.add(
                    Finding(
                        filePath = filePath,
                        lineNumber = 0,
                        ruleName = name,
                        message = "二进制文件不应该提交到版本控制",
                        severity = Severity.BLOCK,
                        codeSnippet = filePath
                    )
                )
            }
        }
        return findings
    }
}