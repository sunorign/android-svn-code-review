package com.codereview.ai

import java.io.File

internal class RuleDocLoader {

    private val SECTION_PATTERN = Regex("^#\\s*(.+)\\s*$")

    internal fun loadAllRuleDocs(): List<RuleDoc> {
        val result = mutableListOf<RuleDoc>()

        // Load built-in rule docs from resources
        result.addAll(loadBuiltInRuleDocs())

        // Load user custom rule docs from ~/.code-review/rule-docs/
        result.addAll(loadUserRuleDocs())

        // Deduplicate: user rule overrides built-in if name conflict
        return deduplicate(result)
    }

    private fun loadBuiltInRuleDocs(): List<RuleDoc> {
        val result = mutableListOf<RuleDoc>()
        val commonPaths = listOf(
            "ai_rules/common/java",
            "ai_rules/common/android"
        )

        for (basePath in commonPaths) {
            val stream = this::class.java.classLoader.getResource(basePath)
            if (stream != null) {
                val dir = File(stream.toURI())
                if (dir.exists() && dir.isDirectory) {
                    dir.listFiles()?.filter { it.extension == "md" }?.forEach { file ->
                        try {
                            val ruleDoc = parseRuleDoc(file.readText(), file.absolutePath)
                            result.add(ruleDoc)
                        } catch (e: Exception) {
                            println("Warning: Failed to parse built-in RuleDoc ${file.path}: ${e.message}")
                        }
                    }
                }
            }
        }

        return result
    }

    private fun loadUserRuleDocs(): List<RuleDoc> {
        val result = mutableListOf<RuleDoc>()
        val homeDir = System.getProperty("user.home")
        val userDir = File(homeDir, ".code-review/rule-docs")

        if (!userDir.exists()) {
            return emptyList()
        }

        userDir.listFiles()?.filter { it.extension == "md" }?.forEach { file ->
            try {
                val ruleDoc = parseRuleDoc(file.readText(), file.absolutePath)
                result.add(ruleDoc)
            } catch (e: Exception) {
                println("Warning: Failed to parse user RuleDoc ${file.path}: ${e.message}")
            }
        }

        return result
    }

    private fun parseRuleDoc(content: String, sourcePath: String): RuleDoc {
        val lines = content.lines()
        var currentSection: String? = null
        val sections = mutableMapOf<String, StringBuilder>()

        for (line in lines) {
            val trimmed = line.trim()
            val match = SECTION_PATTERN.matchEntire(trimmed)
            if (match != null) {
                currentSection = match.groupValues[1].trim().lowercase()
                sections[currentSection] = StringBuilder()
            } else if (currentSection != null) {
                sections[currentSection]!!.appendLine(line)
            }
        }

        val name = sections["规则名"]?.toString()?.trim()
            ?: sourcePath.substringAfterLast("/").substringBeforeLast(".")
        val tagsStr = sections["标签"]?.toString()?.trim().orEmpty()
        val tags = tagsStr.split(",").map { it.trim() }.filter { it.isNotEmpty() }

        // Combine all remaining content into full document
        val contentBuilder = StringBuilder()
        sections.forEach { (section, builder) ->
            contentBuilder.appendLine("# $section")
            contentBuilder.appendLine(builder.toString().trim())
            contentBuilder.appendLine()
        }

        return RuleDoc(
            name = name,
            tags = tags,
            content = contentBuilder.toString().trim(),
            sourcePath = sourcePath
        )
    }

    private fun deduplicate(ruleDocs: List<RuleDoc>): List<RuleDoc> {
        // Last occurrence (user) wins
        return ruleDocs.reversed().distinctBy { it.name }.reversed()
    }
}