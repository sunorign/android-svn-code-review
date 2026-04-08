package com.codereview.cli

import com.codereview.core.BaseRule
import com.codereview.core.Scanner
import com.codereview.core.Finding
import com.codereview.ai.AiClient
import com.codereview.ai.AiConfigLoader
import com.codereview.ai.AiClientFactory
import com.codereview.ai.PromptLoader
import com.codereview.rules.RuleLoader
import com.codereview.report.ReviewResult
import com.codereview.report.HtmlReport
import com.codereview.report.MarkdownReport
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.options.option
import com.github.ajalt.clikt.parameters.options.default
import java.io.File
import java.time.Instant
import java.time.format.DateTimeFormatter
import java.time.LocalDateTime
import kotlinx.coroutines.runBlocking

internal class CliMain : CliktCommand(name = "CodeReview", help = "Code Review - Android 代码审查工具") {
    private val project by option("--project", help = "项目名称 (payment/cashier/mis/mtms)").default("payment")
    private val outputDir by option("--output", help = "输出目录").default(".")

    override fun run() {
        val startTime = Instant.now().toEpochMilli()

        println("Starting Code Review...")
        println("Project: $project")

        // Load rules from local settings
        val ruleLoader = RuleLoader()
        val localRuleSettings = com.codereview.rules.LocalRuleSettingsLoader.loadSettings()
        val rules = ruleLoader.loadEnabledRules(localRuleSettings)
        val localEnabled = localRuleSettings.localEnabled
        println("Loaded ${rules.size} enabled rules")

        // Scan current directory
        val scanner = Scanner()
        val baseDir = File(".").absoluteFile
        val files = scanner.scanProject(baseDir)
        println("Scanned ${files.size} Java/Kotlin files")

        // Run local rules
        val localFindings = mutableListOf<Finding>()
        if (localEnabled) {
            for (file in files) {
                try {
                    val content = file.readText()
                    val relativePath = baseDir.toPath().relativize(file.toPath()).toString()
                    for (rule in rules) {
                        val findings = rule.checkFullFile(relativePath, content)
                        localFindings.addAll(findings)
                    }
                } catch (e: Exception) {
                    println("Warning: Failed to read file ${file.absolutePath}: ${e.message}")
                }
            }
        }

        println("Local check done, found ${localFindings.size} findings")

        // AI review (if configured)
        val aiFindings = mutableListOf<com.codereview.ai.AiFinding>()
        var aiEnabled = false
        var aiConfig: com.codereview.ai.AiConfig? = null
        var prompt: String? = null
        var promptFiles: List<String> = emptyList()
        var aiResponse: com.codereview.ai.AiResponse? = null
        try {
            aiConfig = AiConfigLoader.loadConfig()
            aiEnabled = aiConfig.aiEnabled

            if (aiEnabled) {
                val aiClient = AiClientFactory.create(aiConfig)
                val promptLoader = PromptLoader()
                val loadedPrompt = promptLoader.getCommonFullReviewPrompt()
                prompt = loadedPrompt.content
                promptFiles = loadedPrompt.loadedFiles

                // For simplicity, combine first 10 files
                val codeContent = files.take(10).joinToString("\n\n---\n\n") { file ->
                    val relativePath = baseDir.toPath().relativize(file.toPath()).toString()
                    "--- $relativePath ---\n${file.readText().take(2000)}"
                }

                println("Starting AI review with ${aiConfig.provider} provider...")

                // AI review is blocking
                aiResponse = runBlocking {
                    aiClient.review(prompt, codeContent)
                }

                if (aiResponse.success) {
                    aiFindings.addAll(aiResponse.findings)
                    println("AI review done, found ${aiResponse.findings.size} findings")
                } else {
                    println("AI review failed: ${aiResponse.errorMessage}")
                }
            } else {
                println("AI review disabled in configuration")
            }
        } catch (e: Exception) {
            println("AI review skipped: ${e.message}")
        }

        val endTime = Instant.now().toEpochMilli()
        val duration = endTime - startTime

        // Generate reports
        val result = ReviewResult(
            localFindings = localFindings,
            aiFindings = aiFindings,
            projectName = project,
            scannedFiles = files.size,
            durationMs = duration,
            aiEnabled = aiEnabled,
            localEnabled = localEnabled,
            scanMode = "Full Scan",
            enabledRules = rules.map { it.name },
            loadedRules = rules,
            aiProvider = if (aiEnabled) aiConfig?.provider else null,
            aiModel = if (aiEnabled) aiConfig?.model else null,
            aiPrompt = if (aiEnabled) prompt else null,
            aiPromptFiles = if (aiEnabled) promptFiles else emptyList(),
            aiRawResponse = if (aiEnabled) aiResponse?.rawResponse else null,
            aiDebugInfo = if (aiEnabled) {
                buildString {
                    aiConfig?.let { config ->
                        appendLine("AI Provider: ${config.provider}")
                        appendLine("AI Model: ${config.model}")
                        appendLine("API URL: ${config.apiUrl}")
                        appendLine("Max Tokens: ${config.maxTokens}")
                        appendLine("Timeout: ${config.timeoutSeconds}s")
                        appendLine("Local Enabled: $localEnabled")
                    }
                    aiResponse?.let { response ->
                        appendLine("Response Status: ${if (response.success) "Success" else "Failure"}")
                        if (!response.success) {
                            appendLine("Error: ${response.errorMessage}")
                        }
                    }
                }
            } else null,
            aiExpectedTotal = if (aiEnabled) aiResponse?.expectedTotal else null,
            aiParsingDebug = if (aiEnabled) aiResponse?.parsingDebug ?: emptyList() else emptyList(),
            scannedFilePaths = files
        )

        val outputDirFile = File(outputDir)
        outputDirFile.mkdirs()

        val generators = listOf(
            HtmlReport(),
            MarkdownReport()
        )

        val timestamp = DateTimeFormatter
            .ofPattern("yyyyMMdd-HHmmss")
            .format(LocalDateTime.now())

        for (generator in generators) {
            val outputFile = File(outputDirFile, "code-review-result-$timestamp.${generator.extension}")
            generator.generate(result, outputFile)
            println("Report generated: ${outputFile.absolutePath}")
        }

        val blockCount = localFindings.count { it.severity == com.codereview.core.Severity.BLOCK }
        if (blockCount > 0) {
            println("\nFound $blockCount BLOCK issues, review failed!")
            System.exit(1)
        }

        println("\nReview completed successfully!")
    }
}

fun main(args: Array<String>) = CliMain().main(args)