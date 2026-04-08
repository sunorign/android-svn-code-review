package com.codereview.ai

import kotlinx.serialization.Serializable
import com.codereview.ai.providers.ClaudeClient
import com.codereview.ai.providers.OpenRouterClient
import com.codereview.ai.providers.OllamaClient

data class AiResponse(
    val success: Boolean,
    val findings: List<AiFinding>,
    val expectedTotal: Int? = null,
    val parsingDebug: List<String> = emptyList(),
    val errorMessage: String? = null,
    val rawResponse: String? = null
)

@kotlinx.serialization.Serializable
data class AiFinding(
    val priority: String,      // 严重/一般/轻微
    val issueType: String,     // 问题分类
    val location: String,      // 文件路径:行号
    val description: String,   // 详细描述
    val suggestion: String,    // 修复建议
    val alwaysDisplay: Boolean = false
)

interface AiClient {
    suspend fun review(prompt: String, codeContent: String): AiResponse
    suspend fun testConnection(prompt: String): TestResponse
}

data class TestResponse(
    val success: Boolean,
    val responseText: String,
    val errorMessage: String? = null,
    val rawResponse: String? = null
)

object AiClientFactory {
    fun create(config: AiConfig): AiClient {
        return when (config.provider.lowercase()) {
            "claude" -> ClaudeClient(config)
            "openrouter" -> OpenRouterClient(config)
            "ollama" -> OllamaClient(config)
            else -> throw IllegalArgumentException("Unknown provider: ${config.provider}")
        }
    }
}
