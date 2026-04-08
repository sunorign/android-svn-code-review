package com.codereview.rules

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File

@Serializable
internal data class RuleState(
    val className: String,
    val displayName: String,
    val description: String,
    val enabled: Boolean,
    val groupName: String
)

@Serializable
internal data class LocalRuleSettings(
    val localEnabled: Boolean,
    val rules: List<RuleState>
)

internal object LocalRuleSettingsLoader {
    private val settingsDir = File(System.getProperty("user.home"), ".code-review")
    private val settingsFile = File(settingsDir, "local_rules.json")

    private val json = Json {
        prettyPrint = true
        ignoreUnknownKeys = true
    }

    fun loadSettings(): LocalRuleSettings {
        if (!settingsFile.exists()) {
            val defaultSettings = createDefaultSettings()
            saveSettings(defaultSettings)
            return defaultSettings
        }

        return try {
            json.decodeFromString<LocalRuleSettings>(settingsFile.readText())
        } catch (e: Exception) {
            // If corrupted, create default
            val defaultSettings = createDefaultSettings()
            saveSettings(defaultSettings)
            defaultSettings
        }
    }

    fun saveSettings(settings: LocalRuleSettings) {
        settingsDir.mkdirs()
        settingsFile.writeText(json.encodeToString(LocalRuleSettings.serializer(), settings))
    }

    private fun createDefaultSettings(): LocalRuleSettings {
        val allRules = discoverAllRules()
        return LocalRuleSettings(
            localEnabled = true,
            rules = allRules
        )
    }

    fun discoverAllRules(): List<RuleState> {
        val rules = mutableListOf<RuleState>()

        // Add common rules
        val commonRules = listOf(
            "com.codereview.rules.common.java.JavaDebugLoggingRule" to RuleInfo("Java-DebugLogging", "检测调试日志输出 (System.out.println, Log.d/Log.v)"),
            "com.codereview.rules.common.java.JavaHardcodedSecretsRule" to RuleInfo("Java-HardcodedSecrets", "检测硬编码密码、密钥和API Key"),
            "com.codereview.rules.common.java.JavaUnclosedResourcesRule" to RuleInfo("Java-UnclosedResources", "检查未关闭的 Cursor、Stream、Connection 资源"),
            "com.codereview.rules.common.java.JavaNpeRiskRule" to RuleInfo("Java-NPERisk", "识别多层调用可能导致的空指针异常"),
            "com.codereview.rules.common.java.JavaMemoryLeakRule" to RuleInfo("Java-MemoryLeak", "检测可能导致内存泄漏的非静态内部类"),
            "com.codereview.rules.common.android.AndroidHardcodedUrlsRule" to RuleInfo("Android-HardcodedUrls", "检查硬编码IP地址或URL"),
            "com.codereview.rules.common.android.AndroidViewHolderPatternRule" to RuleInfo("Android-ViewHolderPattern", "验证是否正确使用ViewHolder模式"),
            "com.codereview.rules.common.android.AndroidBinaryFilesRule" to RuleInfo("Android-BinaryFiles", "阻止二进制文件 (.apk/.dex/.aar/.so) 提交")
        )
        commonRules.forEach { (className, info) ->
            rules.add(RuleState(className, info.displayName, info.description, enabled = true, groupName = "通用规则"))
        }

        // Check for project-specific rules from each project's rules.json
        val projects = listOf("payment", "cashier", "mis", "mtms")
        for (project in projects) {
            val configPath = "/com/codereview/rules/projects/$project/rules.json"
            val stream = RuleLoader::class.java.getResourceAsStream(configPath)
            if (stream != null) {
                try {
                    val configJson = stream.bufferedReader().use { it.readText() }
                    val config = json.decodeFromString<RuleConfig>(configJson)
                    config.enabledRules.forEach { className ->
                        // Check if already added (common rules can be in project config)
                        if (rules.none { it.className == className }) {
                            val displayName = className.substringAfterLast(".")
                            val description = "项目特定规则: $className"
                            rules.add(RuleState(className, displayName, description, enabled = true, groupName = "项目规则 - $project"))
                        }
                    }
                } catch (e: Exception) {
                    // Ignore, skip this project
                }
            }
        }

        return rules
    }

    private data class RuleInfo(
        val displayName: String,
        val description: String
    )
}
