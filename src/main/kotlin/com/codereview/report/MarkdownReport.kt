package com.codereview.report

import com.codereview.core.Finding
import com.codereview.ai.AiFinding
import java.io.File

internal class MarkdownReport : ReportGenerator {

    override val extension = "log"

    override fun generate(result: ReviewResult, outputFile: File) {
        val content = buildString {
            appendLine("Code Review 报告")
            appendLine("=".repeat(50))
            appendLine()

            appendLine("[基本信息]")
            appendLine()
            appendLine("项目名称: ${result.projectName}")
            appendLine("扫描时间: ${result.timestamp}")
            appendLine("持续时间: ${result.durationMs}ms")
            appendLine("扫描文件数: ${result.scannedFiles}")
            appendLine("扫描模式: ${result.scanMode}")
            appendLine()

            appendLine("[分析文件列表]")
            appendLine()
            if (result.scannedFilePaths.isEmpty()) {
                appendLine("未记录文件列表")
            } else {
                val fileCount = result.scannedFilePaths.size
                if (fileCount <= 15) {
                    // List all files when few
                    result.scannedFilePaths.forEachIndexed { index, file ->
                        appendLine("${index + 1}. ${file.path}")
                    }
                } else {
                    // Group by package when many
                    val grouped = result.scannedFilePaths
                        .groupBy { file ->
                            // Extract package from file path
                            // Example: "com/payment/appconst/Constants.java" -> "com.payment.appconst"
                            // Take everything except the filename, convert dots
                            val lastSlashIndex = file.path.indexOfLast { it == '/' || it == '\\' }
                            if (lastSlashIndex >= 0) {
                                val packagePath = file.path.substring(0, lastSlashIndex)
                                packagePath.replace(Regex("[\\\\/]"), ".")
                            } else {
                                // No slash, just use the directory name
                                file.parentFile?.name ?: "unknown"
                            }
                        }
                    grouped.entries.forEachIndexed { index, entry ->
                        val packageName = entry.key
                        val count = entry.value.size
                        if (count == 1) {
                            appendLine("${index + 1}. ${entry.value.first().path}")
                        } else {
                            appendLine("${index + 1}. $packageName.* ($count 个文件)")
                        }
                    }
                }
            }

            appendLine()

            appendLine("[统计]")
            appendLine()
            appendLine("本地规则发现问题: ${result.localFindings.size} 个")
            appendLine("AI 发现问题: ${result.aiFindings.size} 个")
            appendLine()

            appendLine("[启用规则列表]")
            appendLine()
            if (!result.localEnabled) {
                appendLine("本地规则审查: 已禁用")
            } else if (result.enabledRules.isEmpty()) {
                appendLine("未启用任何规则。")
            } else {
                result.enabledRules.forEachIndexed { index, rule ->
                    appendLine("${index + 1}. $rule")
                }
            }
            appendLine()

            if (result.aiEnabled) {
                appendLine("[AI 配置信息]")
                appendLine()
                appendLine("AI 提供商: ${result.aiProvider ?: "未配置"}")
                appendLine("AI 模型: ${result.aiModel ?: "未配置"}")
                appendLine("AI 状态: 已启用")
                appendLine()

                appendLine("[AI 提示词]")
                appendLine()
                if (result.aiPromptFiles.isNotEmpty()) {
                    result.aiPromptFiles.forEachIndexed { index, path ->
                        appendLine("${index + 1}. $path")
                    }
                } else {
                    appendLine("未加载自定义提示词，仅使用通用提示词")
                }
                appendLine()

                appendLine("[AI 完整响应]")
                appendLine()
                if (result.aiRawResponse != null) {
                    appendLine("-".repeat(60))
                    // No escaping - leave raw content as-is
                    val cleanedResponse = result.aiRawResponse.lines()
                        .filter { it.isNotBlank() || it.isNotEmpty() }
                        .joinToString("\n") { it }
                    appendLine(cleanedResponse)
                    appendLine("-".repeat(60))
                } else {
                    appendLine("未获取到完整响应。")
                }
                appendLine()
            }

            // Always include AI debug info
            appendLine("[AI 调试信息]")
            appendLine()
            appendLine("AI 启用: ${result.aiEnabled}")
            appendLine("本地规则启用: ${result.localEnabled}")
            appendLine("AI 提供商: ${result.aiProvider ?: "未配置"}")
            appendLine("AI 模型: ${result.aiModel ?: "未配置"}")
            appendLine("API 地址: ${if (result.aiDebugInfo?.contains("API URL:") == true) result.aiDebugInfo.lines().find { it.startsWith("API URL:") }?.substringAfter("API URL:")?.trim() ?: "未配置" else "未配置"}")

            // Determine response status
            val responseStatus = when {
                !result.aiEnabled -> "未启用"
                result.aiErrorMessage != null -> "失败"
                result.aiFindings.isNotEmpty() -> "成功"
                else -> "未知"
            }
            appendLine("响应状态: $responseStatus")

            if (result.aiErrorMessage != null) {
                appendLine("错误信息: ${result.aiErrorMessage}")
            }

            // Add expected vs parsed count info
            result.aiRawResponse?.let { raw ->
                // Extract expected vs actual if present
                val expectedMatch = Regex("Expected.*?(\\d+)").find(raw)
                val parsedMatch = Regex("Parsed.*?(\\d+)").find(raw)
                if (expectedMatch != null && parsedMatch != null) {
                    appendLine("Expected findings: ${expectedMatch.groupValues[1]}")
                    appendLine("Parsed findings: ${parsedMatch.groupValues[1]}")
                }
            }

            if (result.aiDebugInfo != null) {
                appendLine()
                appendLine("[详细调试信息]")
                appendLine()
                appendLine("-".repeat(40))
                appendLine(result.aiDebugInfo)
                appendLine("-".repeat(40))
            }
            appendLine()

            // 输出 AI 解析调试日志
            if (result.aiParsingDebug.isNotEmpty()) {
                appendLine("[AI 解析调试日志]")
                appendLine()
                appendLine("-".repeat(60))
                result.aiParsingDebug.forEach { line ->
                    appendLine(line)
                }
                appendLine("-".repeat(60))
                appendLine()
            }

            if (result.localFindings.isEmpty() && result.aiFindings.isEmpty()) {
                appendLine("[检查结果]")
                appendLine()
                appendLine("未发现任何问题")
                appendLine()
            }
        }

        outputFile.writeText(content)
    }
}