package com.codereview.ai

import java.util.regex.Pattern

/**
 * Analyze code content to extract keywords for tag matching.
 *
 * Goal: Extract relevant identifiers from code that can match against RuleDoc tags.
 */
class QueryAnalyzer {

    // Common Java/Kotlin keywords to ignore
    private val commonKeywords = setOf(
        // Java/Kotlin keywords
        "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class",
        "const", "continue", "default", "do", "double", "else", "enum", "extends", "final",
        "finally", "float", "for", "goto", "if", "implements", "import", "instanceof", "int",
        "interface", "long", "native", "new", "package", "private", "protected", "public",
        "return", "short", "static", "strictfp", "super", "switch", "synchronized", "this",
        "throw", "throws", "transient", "try", "void", "volatile", "while",
        // Kotlin specific
        "val", "var", "fun", "object", "companion", "data", "sealed", "inner", "inline",
        "infix", "operator", "tailrec", "external", "suspend", "actual", "expect",
        "crossinline", "noinline", "out", "reified", "typealias", "where", "by", "get", "set",
        // Android common
        "android", "app", "content", "view", "layout", "widget", "button", "text", "drawable",
        "bitmap", "color", "string", "int", "boolean", "void", "override",
        // Common short words that don't help matching
        "get", "set", "is", "to", "of", "in", "on", "it", "the", "and", "for", "with", "that"
    )

    // Identifier pattern - matches camelCase, snake_case
    private val identifierPattern = Pattern.compile("[a-zA-Z][a-zA-Z0-9]*")

    /**
     * Extract keywords from code content for tag matching.
     * @param codeContent The source code to analyze
     * @return Lowercase list of extracted keywords (unique, filtered)
     */
    fun extractKeywords(codeContent: String): Set<String> {
        val result = mutableSetOf<String>()

        // Split into identifiers using regex
        val matcher = identifierPattern.matcher(codeContent)
        while (matcher.find()) {
            val identifier = matcher.group()
            if (identifier.length < 2) continue // Skip too short

            // Split camelCase and snake_case into words
            val words = splitIdentifier(identifier)
            for (word in words) {
                val lowerWord = word.lowercase()
                if (lowerWord.length >= 3 && lowerWord !in commonKeywords) {
                    result.add(lowerWord)
                }
            }
        }

        return result
    }

    /**
     * Split identifier into words - handles camelCase and snake_case.
     */
    private fun splitIdentifier(identifier: String): List<String> {
        val words = mutableListOf<String>()
        val current = StringBuilder()

        for (char in identifier) {
            when {
                // underscore separates words in snake_case
                char == '_' -> {
                    if (current.isNotEmpty()) {
                        words.add(current.toString())
                        current.clear()
                    }
                }
                // uppercase starts new word in camelCase
                char.isUpperCase() && current.isNotEmpty() -> {
                    words.add(current.toString())
                    current.clear()
                    current.append(char.lowercaseChar())
                }
                else -> {
                    current.append(char)
                }
            }
        }

        if (current.isNotEmpty()) {
            words.add(current.toString())
        }

        return words
    }

    /**
     * Filter RuleDocs that match the extracted keywords.
     * @param ruleDocs All available rule documents
     * @param extractedKeywords Keywords extracted from code
     * @param matchThreshold Minimum number of matching tags required (default = 1)
     * @return Filtered list of matching RuleDocs
     */
    fun filterMatchingRules(ruleDocs: List<RuleDoc>, extractedKeywords: Set<String>, matchThreshold: Int = 1): List<RuleDoc> {
        if (extractedKeywords.isEmpty()) {
            return ruleDocs // If no keywords extracted, return all
        }

        return ruleDocs.filter { rule ->
            val ruleTags = rule.tags.map { it.lowercase() }.toSet()
            val matches = extractedKeywords.intersect(ruleTags).size
            matches >= matchThreshold
        }
    }
}
