package com.codereview.report

import com.codereview.core.Finding
import com.codereview.ai.AiFinding
import com.codereview.core.BaseRule
import java.io.File

internal data class ReviewResult(
    val localFindings: List<Finding>,
    val aiFindings: List<AiFinding>,
    val projectName: String,
    val scannedFiles: Int,
    val durationMs: Long,
    val timestamp: String = java.time.format.DateTimeFormatter
        .ofPattern("yyyyMMdd-HHmmss")
        .format(java.time.LocalDateTime.now()),
    val aiEnabled: Boolean,
    val localEnabled: Boolean,
    val scanMode: String = "Full Scan",
    val enabledRules: List<String> = emptyList(),
    val loadedRules: List<BaseRule> = emptyList(),
    val aiProvider: String? = null,
    val aiModel: String? = null,
    val aiPrompt: String? = null,
    val aiPromptFiles: List<String> = emptyList(),
    val aiRawResponse: String? = null,
    val aiDebugInfo: String? = null,
    val aiErrorMessage: String? = null,
    val aiExpectedTotal: Int? = null,
    val aiParsingDebug: List<String> = emptyList(),
    val scannedFilePaths: List<java.io.File> = emptyList()
)

internal interface ReportGenerator {
    fun generate(result: ReviewResult, outputFile: File)
    val extension: String
}
