package com.codereview.ai

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.BufferedReader
import java.io.File

@Serializable
data class AiConfig(
    val provider: String,
    val apiKey: String,
    val apiUrl: String,
    val model: String,
    val maxTokens: Int,
    val timeoutSeconds: Int = 60,
    val aiEnabled: Boolean = true
)

object AiConfigLoader {

    private val json = Json { prettyPrint = true }

    fun loadConfig(): AiConfig {
        val userConfigFile = getUserConfigFile()
        return if (userConfigFile.exists()) {
            val jsonText = userConfigFile.readText()
            json.decodeFromString<AiConfig>(jsonText)
        } else {
            // Load default from resources
            loadDefaultConfig()
        }
    }

    fun saveConfig(config: AiConfig) {
        val userConfigFile = getUserConfigFile()
        val configDir = userConfigFile.parentFile
        if (!configDir.exists()) {
            configDir.mkdirs()
        }
        val jsonText = json.encodeToString(AiConfig.serializer(), config)
        userConfigFile.writeText(jsonText)
    }

    fun getUserConfigFile(): File {
        val homeDir = System.getProperty("user.home")
        return File(homeDir, ".code-review/ai_config.json")
    }

    private fun loadDefaultConfig(): AiConfig {
        val stream = this::class.java.classLoader.getResourceAsStream("ai_config/ai_client_config.json")
        return if (stream != null) {
            val json = stream.bufferedReader().use { it.readText() }
            Json.decodeFromString<AiConfig>(json)
        } else {
            // Default empty config if resource not found
            AiConfig(
                provider = "claude",
                apiKey = "",
                apiUrl = "https://api.anthropic.com/v1/messages",
                model = "claude-3-opus-20240229",
                maxTokens = 4096,
                timeoutSeconds = 60,
                aiEnabled = true
            )
        }
    }
}
