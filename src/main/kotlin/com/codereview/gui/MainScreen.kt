package com.codereview.gui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.codereview.core.Scanner
import com.codereview.core.Finding
import com.codereview.ai.AiConfigLoader
import com.codereview.ai.AiClientFactory
import com.codereview.ai.PromptLoader
import com.codereview.core.DiffGranularity
import com.codereview.core.ScanMode
import com.codereview.core.ScanSettings
import com.codereview.core.ScanSettingsLoader
import com.codereview.core.AppSettingsLoader
import com.codereview.gui.AiSettingsDialog
import com.codereview.gui.ScanSettingsDialog
import com.codereview.gui.LocalRulesSettingsDialog
import com.codereview.rules.RuleLoader
import com.codereview.rules.LocalRuleSettings
import com.codereview.rules.LocalRuleSettingsLoader
import com.codereview.report.HtmlReport
import com.codereview.report.MarkdownReport
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.awt.Desktop
import java.io.File
import java.time.Instant
import java.time.format.DateTimeFormatter
import java.time.LocalDateTime
import javax.swing.JFileChooser
import javax.swing.filechooser.FileSystemView

@Composable
internal fun MainScreen() {
    var selectedDir by remember { mutableStateOf("") }
    var isReviewing by remember { mutableStateOf(false) }
    var progressText by remember { mutableStateOf("") }
    var resultText by remember { mutableStateOf("") }
    var showAiSettingsDialog by remember { mutableStateOf(false) }
    var showScanSettingsDialog by remember { mutableStateOf(false) }
    var showLocalRulesSettingsDialog by remember { mutableStateOf(false) }
    var scanSettings by remember { mutableStateOf(ScanSettingsLoader.loadSettings()) }

    val coroutineScope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.Top,
        horizontalAlignment = Alignment.Start
    ) {
        // Header with title and settings buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Code Review", style = MaterialTheme.typography.headlineLarge)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = { showScanSettingsDialog = true }) {
                    Text("扫描设置")
                }
                OutlinedButton(onClick = { showLocalRulesSettingsDialog = true }) {
                    Text("本地设置")
                }
                OutlinedButton(onClick = { showAiSettingsDialog = true }) {
                    Text("AI 设置")
                }
            }
        }
        Spacer(modifier = Modifier.height(16.dp))

        // Directory selection
        Text("选择项目目录:", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(4.dp))
        Row {
            OutlinedTextField(
                value = selectedDir,
                onValueChange = { selectedDir = it },
                modifier = Modifier.weight(1f),
                placeholder = { Text("点击右侧按钮选择项目根目录") },
                singleLine = true
            )
            Spacer(modifier = Modifier.width(8.dp))
            Button(onClick = {
                val chooser = JFileChooser(FileSystemView.getFileSystemView().homeDirectory)
                chooser.fileSelectionMode = JFileChooser.DIRECTORIES_ONLY
                chooser.dialogTitle = "选择项目目录"
                val result = chooser.showOpenDialog(null)
                if (result == JFileChooser.APPROVE_OPTION) {
                    selectedDir = chooser.selectedFile.absolutePath
                }
            }) {
                Text("浏览...")
            }
        }
        Spacer(modifier = Modifier.height(16.dp))

        // Current scan settings display
        Card {
            Column(
                modifier = Modifier
                    .padding(12.dp)
                    .fillMaxWidth()
            ) {
                val modeText = when (scanSettings.scanMode) {
                    ScanMode.FULL -> "全局扫描"
                    ScanMode.SVN_DIFF -> "SVN Diff"
                    ScanMode.GIT_DIFF -> "Git Diff"
                }
                val displayText = buildString {
                    append("当前扫描模式: $modeText")
                    if (scanSettings.scanMode != ScanMode.FULL) {
                        val granularityText = when (scanSettings.diffGranularity) {
                            DiffGranularity.WHOLE_FILE -> "整个文件"
                            DiffGranularity.CHANGED_LINES -> "仅变更行"
                        }
                        append(" / $granularityText")
                    }
                }
                Text(displayText, style = MaterialTheme.typography.bodyMedium)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Start button
        Button(
            onClick = {
                if (selectedDir.isBlank()) {
                    resultText = "请先选择项目目录"
                    return@Button
                }
                isReviewing = true
                progressText = "开始扫描..."
                resultText = ""

                // Get output directory from settings before starting review
                val appSettings = AppSettingsLoader.loadSettings()
                val outputDir = AppSettingsLoader.getEffectiveOutputDirectory(appSettings)

                coroutineScope.launch(Dispatchers.Default) {
                    val result = runReview(
                        selectedDir,
                        scanSettings,
                        outputDir,
                        onError = { error -> resultText = error },
                        onReviewingChange = { isReviewing = it }
                    )
                    if (result == null) {
                        return@launch
                    }
                    isReviewing = false
                    progressText = ""
                    resultText = "审查完成，共扫描 ${result.scannedFiles} 个文件，发现 ${result.localFindings.size} 个本地问题，${result.aiFindings.size} 个AI问题\n"
                    resultText += "报告已保存到目录:\n$outputDir\n"
                    if (result.aiEnabled && result.aiErrorMessage != null) {
                        resultText += "\nAI 审查失败：${result.aiErrorMessage}\n"
                    }

                    // Open HTML report in browser
                    try {
                        val htmlFile = getOutputFile(result.timestamp, "html", outputDir.absolutePath)
                        if (htmlFile.exists()) {
                            Desktop.getDesktop().browse(htmlFile.toURI())
                        }
                    } catch (e: Exception) {
                        // ignore
                    }
                }
            },
            modifier = Modifier.fillMaxWidth(),
            enabled = !isReviewing && selectedDir.isNotBlank()
        ) {
            Text(if (isReviewing) "审查中..." else "开始代码审查")
        }
        Spacer(modifier = Modifier.height(16.dp))

        // Progress
        if (progressText.isNotBlank()) {
            LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(8.dp))
            Text(progressText)
            Spacer(modifier = Modifier.height(16.dp))
        }

        // Result
        if (resultText.isNotBlank()) {
            Card {
                Column(
                    modifier = Modifier
                        .padding(16.dp)
                        .fillMaxWidth()
                ) {
                    Text(resultText, style = MaterialTheme.typography.bodyLarge)
                }
            }
        }
    }

    // AI Settings Dialog
    if (showAiSettingsDialog) {
        AiSettingsDialog(
            onDismiss = { showAiSettingsDialog = false },
            onSaved = { showAiSettingsDialog = false }
        )
    }

    // Scan Settings Dialog
    if (showScanSettingsDialog) {
        ScanSettingsDialog(
            onDismiss = { showScanSettingsDialog = false },
            onSaved = {
                scanSettings = ScanSettingsLoader.loadSettings()
                showScanSettingsDialog = false
            }
        )
    }

    // Local Rules Settings Dialog
    if (showLocalRulesSettingsDialog) {
        LocalRulesSettingsDialog(
            onDismiss = { showLocalRulesSettingsDialog = false },
            onSaved = { showLocalRulesSettingsDialog = false }
        )
    }
}

private suspend fun runReview(
    projectDir: String,
    scanSettings: com.codereview.core.ScanSettings,
    outputDir: File,
    onError: (String) -> Unit,
    onReviewingChange: (Boolean) -> Unit
): com.codereview.report.ReviewResult? {
    val startTime = Instant.now().toEpochMilli()
    val baseDir = File(projectDir)

    // Load settings
    val aiConfig = AiConfigLoader.loadConfig()
    val localRuleSettings = com.codereview.rules.LocalRuleSettingsLoader.loadSettings()
    val localEnabled = localRuleSettings.localEnabled

    if (!aiConfig.aiEnabled && !localEnabled) {
        // Both disabled, cannot start scan
        // We need to return to UI with error message on main thread
        kotlinx.coroutines.withContext(Dispatchers.Main) {
            onError("错误：至少需要开启本地规则审查或 AI 审查其中一项才能开始扫描")
            onReviewingChange(false)
        }
        return null
    }

    // Load rules based on user settings
    val ruleLoader = RuleLoader()
    val rules = ruleLoader.loadEnabledRules(localRuleSettings)

    // Scan
    val scanner = Scanner()
    val files = scanner.scan(baseDir, scanSettings)

    // Local rules - only run if localEnabled
    val localFindings = mutableListOf<Finding>()
    if (localEnabled) {
        for ((index, file) in files.withIndex()) {
            if (index % 10 == 0) {
                // TODO: Update progress
            }
            try {
                val content = file.readText()
                val relativePath = baseDir.toPath().relativize(file.toPath()).toString()
                for (rule in rules) {
                    val findings = rule.checkFullFile(relativePath, content)
                    localFindings.addAll(findings)
                }
            } catch (e: Exception) {
                // Skip unreadable files
            }
        }
    }

    // AI review
    val aiFindings = mutableListOf<com.codereview.ai.AiFinding>()
    var aiEnabled = false
    var prompt: String? = null
    var promptFiles: List<String> = emptyList()
    var aiResponse: com.codereview.ai.AiResponse? = null
    var aiErrorMessage: String? = null
    try {
        aiEnabled = aiConfig.aiEnabled

        if (aiEnabled) {
            val aiClient = AiClientFactory.create(aiConfig)
            val promptLoader = PromptLoader()
            val loadedPrompt = promptLoader.getCommonFullReviewPrompt()
            prompt = loadedPrompt.content
            promptFiles = loadedPrompt.loadedFiles

            // Take first 10 files for AI review
            val codeContent = files.take(10).joinToString("\n\n---\n\n") { file ->
                val relativePath = baseDir.toPath().relativize(file.toPath()).toString()
                try {
                    "--- $relativePath ---\n${file.readText().take(2000)}"
                } catch (e: Exception) {
                    "--- $relativePath ---\n" // Skip unreadable file
                }
            }

            aiResponse = aiClient.review(prompt, codeContent)
            if (aiResponse.success) {
                aiFindings.addAll(aiResponse.findings)
            } else {
                aiErrorMessage = aiResponse.errorMessage
            }
        }
    } catch (e: Exception) {
        aiErrorMessage = e.message
        // AI review optional, just continue
    }

    val endTime = Instant.now().toEpochMilli()
    val duration = endTime - startTime
    val timestamp = DateTimeFormatter
        .ofPattern("yyyyMMdd-HHmmss")
        .format(LocalDateTime.now())

    val result = com.codereview.report.ReviewResult(
        localFindings = localFindings,
        aiFindings = aiFindings,
        projectName = "custom",
        scannedFiles = files.size,
        durationMs = duration,
        timestamp = timestamp,
        aiEnabled = aiEnabled,
        localEnabled = localEnabled,
        scanMode = "Full Scan",
        enabledRules = rules.map { it.name },
        loadedRules = rules,
        aiProvider = if (aiEnabled) aiConfig.provider else null,
        aiModel = if (aiEnabled) aiConfig.model else null,
        aiPrompt = if (aiEnabled) prompt else null,
        aiPromptFiles = if (aiEnabled) promptFiles else emptyList(),
        aiRawResponse = if (aiEnabled) aiResponse?.rawResponse else null,
        aiErrorMessage = aiErrorMessage,
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
                aiErrorMessage?.let { error ->
                    appendLine("Exception Error: $error")
                }
            }
        } else null,
        aiExpectedTotal = if (aiEnabled) aiResponse?.expectedTotal else null,
        aiParsingDebug = if (aiEnabled) aiResponse?.parsingDebug ?: emptyList() else emptyList(),
        scannedFilePaths = files
    )

    outputDir.mkdirs()

    val generators = listOf(
        HtmlReport(),
        MarkdownReport()
    )

    for (generator in generators) {
        val outputFile = getOutputFile(timestamp, generator.extension, outputDir.absolutePath)
        generator.generate(result, outputFile)
    }

    return result
}

private fun getOutputFile(
    timestamp: String,
    extension: String,
    outputDir: String = AppSettingsLoader.getEffectiveOutputDirectory(AppSettingsLoader.loadSettings()).absolutePath
): File {
    return File(outputDir, "code-review-result-$timestamp.$extension")
}
