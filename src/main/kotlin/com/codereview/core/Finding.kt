package com.codereview.core

internal enum class Severity {
    BLOCK, WARNING
}

internal data class Finding(
    val filePath: String,
    val lineNumber: Int,
    val ruleName: String,
    val message: String,
    val severity: Severity,
    val codeSnippet: String
)


