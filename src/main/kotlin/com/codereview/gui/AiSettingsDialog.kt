package com.codereview.gui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import com.codereview.ai.AiConfig
import com.codereview.ai.AiConfigLoader
import com.codereview.ai.AiClientFactory
import com.codereview.ai.TestResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

data class ProviderPreset(
    val providerId: String,
    val displayName: String,
    val defaultApiUrl: String,
    val defaultModel: String,
    val defaultMaxTokens: Int = 4096
)

val PROVIDER_PRESETS = listOf(
    ProviderPreset(
        providerId = "claude",
        displayName = "Anthropic Claude",
        defaultApiUrl = "https://api.anthropic.com/v1/messages",
        defaultModel = "claude-3-opus-20240229"
    ),
    ProviderPreset(
        providerId = "openrouter",
        displayName = "OpenRouter",
        defaultApiUrl = "https://openrouter.ai/api/v1/chat/completions",
        defaultModel = "openai/gpt-4-turbo-preview"
    ),
    ProviderPreset(
        providerId = "ollama",
        displayName = "Local Ollama",
        defaultApiUrl = "http://localhost:11434/api/chat",
        defaultModel = "llama2",
        defaultMaxTokens = 4096
    )
)

@Composable
fun AiSettingsDialog(
    onDismiss: () -> Unit,
    onSaved: () -> Unit,
    onSettingsChanged: (enableTagMatching: Boolean) -> Unit
) {
    var currentConfig by remember { mutableStateOf(AiConfigLoader.loadConfig()) }
    var passwordVisible by remember { mutableStateOf(false) }
    var isSaving by remember { mutableStateOf(false) }
    var isTesting by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var testResult by remember { mutableStateOf<TestResponse?>(null) }
    var enableTagMatching by remember { mutableStateOf(true) }
    val coroutineScope = rememberCoroutineScope()

    // Notify parent when setting changes
    LaunchedEffect(enableTagMatching) {
        onSettingsChanged(enableTagMatching)
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("AI 模型设置") },
        text = {
            Column(
                modifier = Modifier
                    .width(600.dp)
                    .verticalScroll(rememberScrollState())
                    .padding(vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Provider selection
                Text("AI 提供商:", style = MaterialTheme.typography.labelMedium)
                Column(
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    PROVIDER_PRESETS.forEach { preset ->
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            RadioButton(
                                selected = currentConfig.provider == preset.providerId,
                                onClick = {
                                    currentConfig = currentConfig.copy(
                                        provider = preset.providerId,
                                        apiUrl = preset.defaultApiUrl,
                                        model = preset.defaultModel,
                                        maxTokens = preset.defaultMaxTokens
                                    )
                                }
                            )
                            Text(preset.displayName)
                        }
                    }
                }

                // API Key
                Text("API Key:", style = MaterialTheme.typography.labelMedium)
                OutlinedTextField(
                    value = currentConfig.apiKey,
                    onValueChange = { currentConfig = currentConfig.copy(apiKey = it) },
                    visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                    placeholder = { Text("输入你的 API Key") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Start
                ) {
                    Checkbox(
                        checked = passwordVisible,
                        onCheckedChange = { passwordVisible = it }
                    )
                    Text("显示 API Key", style = MaterialTheme.typography.bodyMedium)
                }

                // API URL
                Text("API 地址:", style = MaterialTheme.typography.labelMedium)
                OutlinedTextField(
                    value = currentConfig.apiUrl,
                    onValueChange = { currentConfig = currentConfig.copy(apiUrl = it) },
                    placeholder = { Text("API 服务地址") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )

                // Model name
                Text("模型名称:", style = MaterialTheme.typography.labelMedium)
                OutlinedTextField(
                    value = currentConfig.model,
                    onValueChange = { currentConfig = currentConfig.copy(model = it) },
                    placeholder = { Text("模型名称") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )

                // Max Tokens
                Text("最大 Token 数:", style = MaterialTheme.typography.labelMedium)
                OutlinedTextField(
                    value = currentConfig.maxTokens.takeIf { it > 0 }?.toString() ?: "",
                    onValueChange = {
                        it.toIntOrNull()?.let { tokens ->
                            currentConfig = currentConfig.copy(maxTokens = tokens)
                        }
                    },
                    placeholder = { Text("最大输出 Token 数") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )

                // Timeout Seconds
                Text("超时时间(秒):", style = MaterialTheme.typography.labelMedium)
                OutlinedTextField(
                    value = currentConfig.timeoutSeconds.takeIf { it > 0 }?.toString() ?: "",
                    onValueChange = {
                        it.toIntOrNull()?.let { seconds ->
                            currentConfig = currentConfig.copy(timeoutSeconds = seconds)
                        }
                    },
                    placeholder = { Text("API 请求超时秒数") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )

                // AI Enable toggle
                Text("AI 审查:", style = MaterialTheme.typography.labelMedium)
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Checkbox(
                        checked = currentConfig.aiEnabled,
                        onCheckedChange = {
                            currentConfig = currentConfig.copy(aiEnabled = it)
                        }
                    )
                    Text("开启 AI 审查（关闭后不执行 AI 审查，节省调用费用）", style = MaterialTheme.typography.bodyMedium)
                }

                // Tag matching toggle (for backward compatibility)
                Text("标签检索:", style = MaterialTheme.typography.labelMedium)
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Checkbox(
                        checked = enableTagMatching,
                        onCheckedChange = {
                            enableTagMatching = it
                        }
                    )
                    Text("启用标签检索（只注入相关规则，缩短提示词长度，减少幻觉）", style = MaterialTheme.typography.bodyMedium)
                }
                Spacer(modifier = Modifier.height(8.dp))

                // Retrieval Mode selection
                Text("规则检索模式:", style = MaterialTheme.typography.labelMedium)
                Column(
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    com.codereview.ai.RetrievalMode.values().forEach { mode ->
                        val modeLabel = when (mode) {
                            com.codereview.ai.RetrievalMode.NONE -> "不启用检索（注入所有规则）"
                            com.codereview.ai.RetrievalMode.TAG_MATCHING -> "标签匹配（关键词匹配，默认）"
                            com.codereview.ai.RetrievalMode.SEMANTIC -> "语义检索（RAG，需要 Ollama）"
                        }
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            RadioButton(
                                selected = currentConfig.retrievalMode == mode,
                                onClick = {
                                    currentConfig = currentConfig.copy(retrievalMode = mode)
                                }
                            )
                            Text(modeLabel)
                        }
                    }
                }

                // Warning if semantic selected but not Ollama provider
                if (currentConfig.retrievalMode == com.codereview.ai.RetrievalMode.SEMANTIC && currentConfig.provider != "ollama") {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.secondaryContainer
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            "⚠ 语义检索目前仅支持 Ollama 提供商，使用其他提供商将回退到标签匹配",
                            color = MaterialTheme.colorScheme.onSecondaryContainer,
                            modifier = Modifier.padding(12.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                // Top-N for semantic
                Text("语义检索返回规则数:", style = MaterialTheme.typography.labelMedium)
                OutlinedTextField(
                    value = currentConfig.semanticTopN.takeIf { it > 0 }?.toString() ?: "",
                    onValueChange = {
                        it.toIntOrNull()?.let { n ->
                            currentConfig = currentConfig.copy(semanticTopN = n)
                        }
                    },
                    placeholder = { Text("返回最相关的 N 条规则，默认 10") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )

                // Error message
                errorMessage?.let { error ->
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.errorContainer
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            error,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            modifier = Modifier.padding(12.dp)
                        )
                    }
                }

                // Test result
                testResult?.let { result ->
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = if (result.success) MaterialTheme.colorScheme.secondaryContainer else MaterialTheme.colorScheme.errorContainer
                        ),
                        modifier = Modifier
                            .fillMaxWidth()
                            .heightIn(max = 200.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                if (result.success) "✓ 连接成功" else "✗ 连接失败",
                                style = MaterialTheme.typography.labelMedium,
                                color = if (result.success) MaterialTheme.colorScheme.onSecondaryContainer else MaterialTheme.colorScheme.onErrorContainer
                            )
                            if (!result.success && result.errorMessage != null) {
                                Text(
                                    "错误: ${result.errorMessage}",
                                    color = if (result.success) MaterialTheme.colorScheme.onSecondaryContainer else MaterialTheme.colorScheme.onErrorContainer,
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                            if (result.responseText.isNotBlank()) {
                                Text(
                                    "模型回复:",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = if (result.success) MaterialTheme.colorScheme.onSecondaryContainer else MaterialTheme.colorScheme.onErrorContainer
                                )
                                Text(
                                    result.responseText,
                                    color = if (result.success) MaterialTheme.colorScheme.onSecondaryContainer else MaterialTheme.colorScheme.onErrorContainer,
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                            if (result.rawResponse != null) {
                                Text(
                                    "原始响应 (调试):",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = if (result.success) MaterialTheme.colorScheme.onSecondaryContainer else MaterialTheme.colorScheme.onErrorContainer
                                )
                                Text(
                                    result.rawResponse,
                                    color = if (result.success) MaterialTheme.colorScheme.onSecondaryContainer else MaterialTheme.colorScheme.onErrorContainer,
                                    style = MaterialTheme.typography.bodySmall,
                                    modifier = Modifier.verticalScroll(rememberScrollState())
                                )
                            }
                        }
                    }
                }
            }
        },
        confirmButton = {
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = {
                        errorMessage = null
                        testResult = null
                        isTesting = true
                        coroutineScope.launch(Dispatchers.IO) {
                            try {
                                val aiClient = AiClientFactory.create(currentConfig)
                                val response: TestResponse = aiClient.testConnection("请用一句话简单介绍一下你自己")
                                launch(Dispatchers.Main) {
                                    testResult = response
                                    isTesting = false
                                }
                            } catch (e: Exception) {
                                launch(Dispatchers.Main) {
                                    testResult = TestResponse(
                                        success = false,
                                        responseText = "",
                                        errorMessage = e.message,
                                        rawResponse = null
                                    )
                                    isTesting = false
                                }
                            }
                        }
                    },
                    enabled = !isTesting && !isSaving && currentConfig.aiEnabled && currentConfig.apiKey.isNotBlank() && currentConfig.apiUrl.isNotBlank() && currentConfig.model.isNotBlank() && currentConfig.maxTokens > 0 && currentConfig.timeoutSeconds > 0 && currentConfig.semanticTopN > 0
                ) {
                    Text(if (isTesting) "测试中..." else "测试")
                }
                Button(
                    onClick = {
                        errorMessage = null
                        isSaving = true
                        coroutineScope.launch(Dispatchers.IO) {
                            try {
                                AiConfigLoader.saveConfig(currentConfig)
                                launch(Dispatchers.Main) {
                                    isSaving = false
                                    onSaved()
                                }
                            } catch (e: Exception) {
                                launch(Dispatchers.Main) {
                                    errorMessage = "保存失败: ${e.message}"
                                    isSaving = false
                                }
                            }
                        }
                    },
                    enabled = !isSaving &&
    (!currentConfig.aiEnabled ||
        (currentConfig.apiKey.isNotBlank() &&
         currentConfig.apiUrl.isNotBlank() &&
         currentConfig.model.isNotBlank() &&
         currentConfig.maxTokens > 0 &&
         currentConfig.timeoutSeconds > 0 &&
         currentConfig.semanticTopN > 0))
                ) {
                    Text(if (isSaving) "保存中..." else "保存")
                }
            }
        },
        dismissButton = {
            OutlinedButton(onClick = onDismiss) {
                Text("取消")
            }
        }
    )
}
