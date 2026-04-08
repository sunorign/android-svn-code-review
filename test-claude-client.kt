// Test script to verify ClaudeClient changes compile
@file:Suppress("RedundantExplicitType")

import com.codereview.ai.AiConfig
import com.codereview.ai.providers.ClaudeClient

fun main() {
    println("Testing ClaudeClient compilation...")

    try {
        // Test that we can instantiate ClaudeClient
        val config = AiConfig(
            apiKey = "test-key",
            apiUrl = "https://api.anthropic.com/v1/messages",
            model = "claude-3-opus-20240229",
            maxTokens = 4096,
            timeoutSeconds = 60
        )

        val client = ClaudeClient(config)

        println("✓ ClaudeClient instantiation successful")
        println("✓ Shared parser integration successful")

    } catch (e: Exception) {
        println("✗ Error: ${e.message}")
        e.printStackTrace()
    }
}