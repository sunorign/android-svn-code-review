package com.codereview.rules

import com.codereview.core.BaseRule
import kotlinx.serialization.json.Json
import kotlinx.serialization.Serializable

@Serializable
internal data class RuleConfig(
    val enabledRules: List<String>
)

internal class RuleLoader {
    internal fun loadRules(projectName: String): List<BaseRule> {
        val rules = mutableListOf<BaseRule>()

        val configStream = this::class.java.getResourceAsStream("/com/codereview/rules/projects/$projectName/rules.json")
            ?: return loadCommonRules()

        val configJson = configStream.bufferedReader().use { it.readText() }
        val config = Json.decodeFromString<RuleConfig>(configJson)

        for (ruleClassName in config.enabledRules) {
            try {
                val clazz = Class.forName(ruleClassName)
                val rule = clazz.getDeclaredConstructor().newInstance() as BaseRule
                rules.add(rule)
            } catch (e: Exception) {
                println("Warning: Failed to load rule $ruleClassName: ${e.message}")
            }
        }

        return rules
    }

    internal fun loadEnabledRules(settings: LocalRuleSettings): List<BaseRule> {
        val rules = mutableListOf<BaseRule>()

        for (ruleState in settings.rules) {
            if (!ruleState.enabled) {
                continue
            }
            try {
                val clazz = Class.forName(ruleState.className)
                val rule = clazz.getDeclaredConstructor().newInstance() as BaseRule
                rules.add(rule)
            } catch (e: Exception) {
                println("Warning: Failed to load rule ${ruleState.className}: ${e.message}")
            }
        }

        return rules
    }

    internal fun loadCommonRules(): List<BaseRule> {
        val commonRules = listOf(
            "com.codereview.rules.common.java.JavaDebugLoggingRule",
            "com.codereview.rules.common.java.JavaHardcodedSecretsRule",
            "com.codereview.rules.common.java.JavaUnclosedResourcesRule",
            "com.codereview.rules.common.java.JavaNpeRiskRule",
            "com.codereview.rules.common.java.JavaMemoryLeakRule",
            "com.codereview.rules.common.android.AndroidHardcodedUrlsRule",
            "com.codereview.rules.common.android.AndroidViewHolderPatternRule",
            "com.codereview.rules.common.android.AndroidBinaryFilesRule"
        )

        val rules = mutableListOf<BaseRule>()
        for (className in commonRules) {
            try {
                val clazz = Class.forName(className)
                val rule = clazz.getDeclaredConstructor().newInstance() as BaseRule
                rules.add(rule)
            } catch (e: Exception) {
                println("Warning: Failed to load common rule $className: ${e.message}")
            }
        }

        return rules
    }

    internal fun listProjects(): List<String> {
        return listOf("payment", "cashier", "mis", "mtms")
    }
}