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
