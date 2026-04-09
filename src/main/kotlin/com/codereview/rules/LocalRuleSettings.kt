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
            val loaded = json.decodeFromString<LocalRuleSettings>(settingsFile.readText())
            // Merge with newly discovered rules to pick up any changes in grouping or new rules
            val allDiscovered = discoverAllRules().toMutableList()
            // Keep existing enabled states for rules we already have
            val merged = allDiscovered.map { discovered ->
                val existing = loaded.rules.find { it.className == discovered.className }
                // Use existing enabled state, but update group name from discovery
                existing?.copy(
                    groupName = discovered.groupName,
                    displayName = discovered.displayName,
                    description = discovered.description
                ) ?: discovered
            }
            val result = loaded.copy(rules = merged)
            // Save merged result
            saveSettings(result)
            result
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

        // All known rule classes - we explicitly list them since they're all known at compile time
        val allRuleClassNames = listOf(
            "com.codereview.rules.common.java.JavaDebugLoggingRule",
            "com.codereview.rules.common.java.JavaHardcodedSecretsRule",
            "com.codereview.rules.common.java.JavaUnclosedResourcesRule",
            "com.codereview.rules.common.java.JavaNpeRiskRule",
            "com.codereview.rules.common.java.JavaMemoryLeakRule",
            "com.codereview.rules.common.android.AndroidHardcodedUrlsRule",
            "com.codereview.rules.common.android.AndroidViewHolderPatternRule",
            "com.codereview.rules.common.android.AndroidBinaryFilesRule"
        )

        for (className in allRuleClassNames) {
            try {
                val clazz = Class.forName(className)
                val rule = clazz.getDeclaredConstructor().newInstance() as com.codereview.core.BaseRule
                val groupName = rule.group.displayName
                rules.add(
                    RuleState(
                        className = className,
                        displayName = rule.name,
                        description = rule.description,
                        enabled = true,
                        groupName = groupName
                    )
                )
            } catch (e: Exception) {
                println("Warning: Failed to discover rule $className: ${e.message}")
            }
        }

        return rules
    }
}
