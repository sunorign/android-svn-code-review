package com.codereview.ai

import java.io.File
import java.net.URI
import java.net.URL
import java.net.URLConnection
import java.util.jar.JarEntry
import java.util.jar.JarInputStream

class RuleDocLoader {

    private val SECTION_PATTERN = Regex("^#\\s*(.+)\\s*$")

    fun loadAllRuleDocs(): List<RuleDoc> {
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
            val url = this::class.java.classLoader.getResource(basePath)
            if (url != null) {
                try {
                    // First try: file system access (development mode)
                    val dir = File(url.toURI())
                    if (dir.exists() && dir.isDirectory) {
                        result.addAll(parseDirectory(dir, "built-in"))
                    }
                } catch (e: IllegalArgumentException) {
                    // URI is not hierarchical - probably inside JAR, use JarInputStream
                    try {
                        result.addAll(loadFromJar(url, basePath, "built-in"))
                    } catch (e2: Exception) {
                        println("Warning: Failed to load built-in rules from $basePath: ${e2.message}")
                    }
                } catch (e: Exception) {
                    println("Warning: Failed to load built-in rules from $basePath: ${e.message}")
                }
            }
        }

        return result
    }

    private fun loadUserRuleDocs(): List<RuleDoc> {
        val homeDir = System.getProperty("user.home")
        val userDir = File(homeDir, ".code-review/rule-docs")

        if (!userDir.exists()) {
            return emptyList()
        }

        return parseDirectory(userDir, "user")
    }

    private fun loadFromJar(url: URL, basePath: String, sourceType: String): List<RuleDoc> {
        val result = mutableListOf<RuleDoc>()
        try {
            val connection = url.openConnection() as java.net.JarURLConnection
            val jarFile = connection.jarFile
            jarFile.entries().iterator().forEach { entry ->
                if (entry.name.startsWith(basePath) && entry.name.endsWith(".md")) {
                    try {
                        val content = jarFile.getInputStream(entry).bufferedReader().use { it.readText() }
                        val ruleDoc = parseRuleDoc(content, entry.name)
                        result.add(ruleDoc)
                    } catch (e: Exception) {
                        println("Warning: Failed to parse $sourceType RuleDoc ${entry.name}: ${e.message}")
                    }
                }
            }
        } catch (e: Exception) {
            // Fallback: try another approach - get the jar file from the URL
            try {
                val jarUrlStr = url.toString().substringBefore("!")
                val jarFile = java.util.jar.JarFile(java.io.File(java.net.URI(jarUrlStr)))
                var entry: java.util.jar.JarEntry? = null
                jarFile.entries().iterator().forEach { current ->
                    if (current.name.startsWith(basePath) && current.name.endsWith(".md")) {
                        try {
                            val content = jarFile.getInputStream(current).bufferedReader().use { it.readText() }
                            val ruleDoc = parseRuleDoc(content, current.name)
                            result.add(ruleDoc)
                        } catch (e2: Exception) {
                            println("Warning: Failed to parse $sourceType RuleDoc ${current.name}: ${e2.message}")
                        }
                    }
                }
            } catch (e2: Exception) {
                println("Warning: Failed to load built-in rules from JAR: ${e2.message}")
            }
        }
        return result
    }

    private fun parseDirectory(dir: File, sourceType: String): List<RuleDoc> {
        val result = mutableListOf<RuleDoc>()
        dir.listFiles()?.filter { it.extension == "md" }?.forEach { file ->
            try {
                val ruleDoc = parseRuleDoc(file.readText(), file.absolutePath)
                result.add(ruleDoc)
            } catch (e: Exception) {
                println("Warning: Failed to parse $sourceType RuleDoc ${file.path}: ${e.message}")
            }
        } ?: return emptyList()
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