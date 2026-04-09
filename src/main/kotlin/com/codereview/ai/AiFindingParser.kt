package com.codereview.ai

import java.util.regex.Pattern

internal object AiFindingParser {

    private val FINDINGS_PATTERN = Pattern.compile("<findings>(.*?)</findings>", Pattern.DOTALL)
    // Very permissive matching - handles any whitespace and case variations
    // Need DOTALL so .* matches newlines inside question tags
    private val QUESTION_PATTERN = Pattern.compile("<question\\s*>(.*?)</question\\s*>", Pattern.DOTALL or Pattern.CASE_INSENSITIVE)

    data class ParseResult(
        val findings: List<AiFinding>,
        val expectedTotal: Int?,
        val foundTag: Boolean,
        val debugLog: List<String> = emptyList()
    )

    fun parseFindings(text: String): ParseResult {
        val debugLog = mutableListOf<String>()
        debugLog.add("[AiFindingParser] Starting parsing, total text length: ${text.length}")

        // Extract content between <findings> tags
        val content = extractFindingsContent(text)
        debugLog.add("[AiFindingParser] Extracted <findings> content, length: ${content.length}")

        var expectedTotal: Int? = null
        val findings = mutableListOf<AiFinding>()

        // Each finding wrapped in <question>...</question> tags
        // This is the only supported format now - most stable, no conflicts with any punctuation
        val matcher = QUESTION_PATTERN.matcher(content)
        var matchCount = 0
        while (matcher.find()) {
            matchCount++
            val questionContent = matcher.group(1).orEmpty().trim()
            debugLog.add("[AiFindingParser] Found question #$matchCount, length: ${questionContent.length}")

            if (questionContent.isNotBlank()) {
                try {
                    val finding = parseFinding(questionContent, debugLog)
                    finding?.let {
                        findings.add(it)
                        debugLog.add("[AiFindingParser] Successfully parsed finding: ${it.location}")
                    }
                } catch (e: Exception) {
                    debugLog.add("[AiFindingParser] Failed to parse finding: ${e.message}")
                }
            }
        }

        debugLog.add("[AiFindingParser] Total questions matched: $matchCount, findings parsed: ${findings.size}")

        // Look for total= anywhere
        val totalMatch = Pattern.compile("total\\s*=\\s*(\\d+)").matcher(content)
        if (totalMatch.find()) {
            expectedTotal = totalMatch.group(1)?.toIntOrNull()
            debugLog.add("[AiFindingParser] Found total=: $expectedTotal")
        } else {
            debugLog.add("[AiFindingParser] No total= found")
        }

        return ParseResult(
            findings = findings,
            expectedTotal = expectedTotal,
            foundTag = content.isNotBlank(),
            debugLog = debugLog
        )
    }

    private fun parseFinding(findingContent: String, debugLog: MutableList<String>): AiFinding? {
        // Parse using & as parameter separator
        // Format constraint: & can only be used as separator, content MUST NOT contain &
        // This is enforced by prompt instructions to AI
        val map = mutableMapOf<String, String>()

        // Split on & - since content cannot contain &, simple splitting is safe
        val pairs = mutableListOf<String>()
        val current = StringBuilder()
        var i = 0
        while (i < findingContent.length) {
            val c = findingContent[i]
            if (c == '&') {
                if (current.isNotBlank()) {
                    pairs.add(current.toString())
                    current.clear()
                }
            } else {
                current.append(c)
            }
            i++
        }
        if (current.isNotBlank()) {
            pairs.add(current.toString())
        }

        pairs
            .filter { it.isNotBlank() }
            .forEach { pair ->
                val trimmedPair = pair.trim()
                if (trimmedPair.count { it == '=' } < 1) {
                    debugLog.add("[AiFindingParser]   Skipping pair (no =): '$trimmedPair'")
                    return@forEach
                }
                val (key, value) = trimmedPair.split('=', limit = 2)
                // Clean key: only keep letters, numbers and underscores
                // This handles any extra characters from newlines, escapes, etc.
                val cleanedKey = key.trim()
                    .filter { it.isLetterOrDigit() || it == '_' }
                val cleanedValue = value.trim()
                map[cleanedKey] = cleanedValue
                debugLog.add("[AiFindingParser]   Added key: '$cleanedKey' = '${cleanedValue.take(30)}...'")
            }

        if (map.isEmpty()) {
            debugLog.add("[AiFindingParser]   map is empty, returning null")
            return null
        }

        // Find file_path - be tolerant, sometimes AI adds extra characters (like nfile_path due to newline)
        val location = map.entries.find {
            it.key.contains("file_path") || it.key.contains("location")
        }?.value ?: map["file_path"] ?: map["location"]
        if (location == null) {
            debugLog.add("[AiFindingParser]   file_path not found in map, keys: ${map.keys}")
            return null
        }
        // Find line_start - be tolerant to extra characters
        val lineStartStr = map.entries.find {
            it.key.contains("line_start")
        }?.value ?: map["line_start"]
        val lineStart = lineStartStr?.toIntOrNull()
        if (lineStart == null) {
            debugLog.add("[AiFindingParser]   line_start not found or not a number, keys: ${map.keys}")
            return null
        }
        // Find line_end - be tolerant
        val lineEndStr = map.entries.find {
            it.key.contains("line_end")
        }?.value ?: map["line_end"]
        val lineEnd = lineEndStr?.toIntOrNull() ?: lineStart
        // Find issue_type - be tolerant
        val issueType = map.entries.find {
            it.key.contains("issue_type")
        }?.value ?: map["issue_type"] ?: "BUG"
        // Find severity - be tolerant
        val priority = map.entries.find {
            it.key.contains("severity")
        }?.value ?: map["severity"] ?: "WARNING"
        // Find message - be tolerant
        val description = map.entries.find {
            it.key.contains("message") || it.key.contains("description")
        }?.value ?: map["message"] ?: map["description"] ?: ""
        // Find suggestion - be tolerant
        val suggestion = map.entries.find {
            it.key.contains("suggestion")
        }?.value ?: map["suggestion"] ?: ""
        // Find always_display - be tolerant
        val alwaysDisplay = map.entries.find {
            it.key.contains("always_display")
        }?.value?.toBooleanStrictOrNull() ?: map["always_display"]?.toBooleanStrictOrNull() ?: false

        // Extract metadata - rule_name
        val ruleName = map.entries.find {
            it.key.contains("rule_name") || it.key.contains("rulename")
        }?.value

        // Build metadata
        val metadata = FindingMetadata(
            ruleName = ruleName
        )

        debugLog.add("[AiFindingParser]   Successfully parsed: location=$location, lineStart=$lineStart")
        return AiFinding(
            priority = priority,
            issueType = issueType,
            location = location,
            description = description,
            suggestion = suggestion,
            alwaysDisplay = alwaysDisplay,
            metadata = metadata
        )
    }

    private fun extractFindingsContent(text: String): String {
        val matcher = FINDINGS_PATTERN.matcher(text)
        return if (matcher.find()) {
            matcher.group(1).orEmpty()
        } else {
            // Fallback: if no tag found, use entire text (for backward compatibility)
            text
        }
    }
}
