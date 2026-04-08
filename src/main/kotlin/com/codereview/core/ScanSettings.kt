package com.codereview.core

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File

@Serializable
enum class ScanMode {
    FULL,       // 全局扫描
    SVN_DIFF,   // SVN Diff
    GIT_DIFF    // Git Diff
}

@Serializable
enum class DiffGranularity {
    WHOLE_FILE,         // 检查整个变更文件
    CHANGED_LINES       // 仅检查变更代码行（第一阶段暂不实现功能，只保存配置）
}

@Serializable
data class ScanSettings(
    val scanMode: ScanMode = ScanMode.SVN_DIFF,
    val diffGranularity: DiffGranularity = DiffGranularity.WHOLE_FILE
)

object ScanSettingsLoader {

    private val json = Json { prettyPrint = true }

    fun loadSettings(): ScanSettings {
        val userConfigFile = getUserConfigFile()
        return if (userConfigFile.exists()) {
            val jsonText = userConfigFile.readText()
            json.decodeFromString<ScanSettings>(jsonText)
        } else {
            // 默认值: SVN Diff + 整个文件
            ScanSettings()
        }
    }

    fun saveSettings(settings: ScanSettings) {
        val userConfigFile = getUserConfigFile()
        val configDir = userConfigFile.parentFile
        if (!configDir.exists()) {
            configDir.mkdirs()
        }
        val jsonText = json.encodeToString(ScanSettings.serializer(), settings)
        userConfigFile.writeText(jsonText)
    }

    fun getUserConfigFile(): File {
        val homeDir = System.getProperty("user.home")
        return File(homeDir, ".code-review/scan_settings.json")
    }
}
