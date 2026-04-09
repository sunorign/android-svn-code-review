package com.codereview.core

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File

@Serializable
data class AppSettings(
    val outputDirectory: String? = null
)

object AppSettingsLoader {

    private val json = Json { prettyPrint = true }

    fun loadSettings(): AppSettings {
        val userConfigFile = getUserConfigFile()
        return if (userConfigFile.exists()) {
            val jsonText = userConfigFile.readText()
            json.decodeFromString<AppSettings>(jsonText)
        } else {
            AppSettings()
        }
    }

    fun saveSettings(settings: AppSettings) {
        val userConfigFile = getUserConfigFile()
        val configDir = userConfigFile.parentFile
        if (!configDir.exists()) {
            configDir.mkdirs()
        }
        val jsonText = json.encodeToString(AppSettings.serializer(), settings)
        userConfigFile.writeText(jsonText)
    }

    fun getUserConfigFile(): File {
        val homeDir = System.getProperty("user.home")
        return File(homeDir, ".code-review/app_settings.json")
    }

    /**
     * Get the effective output directory to use.
     * Returns user configured directory if set and valid, otherwise defaults to ~/code-review-output
     */
    fun getEffectiveOutputDirectory(settings: AppSettings): File {
        val configured = settings.outputDirectory
        if (!configured.isNullOrBlank()) {
            return File(configured)
        }
        val homeDir = System.getProperty("user.home")
        return File(homeDir, "code-review-output")
    }
}
