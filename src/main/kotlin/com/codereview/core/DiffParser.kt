package com.codereview.core

internal data class DiffChange(
    val lineNumber: Int,
    val content: String,
    val isAdded: Boolean
)

internal data class FileDiff(
    val filePath: String,
    val changes: List<DiffChange>
)

internal class DiffParser {
    fun parse(svnDiffOutput: String): List<FileDiff> {
        val fileDiffs = mutableListOf<FileDiff>()
        var currentFilePath: String? = null
        val currentChanges = mutableListOf<DiffChange>()
        var currentLineNumber = 0

        for (line in svnDiffOutput.lines()) {
            when {
                line.startsWith("Index: ") -> {
                    if (currentFilePath != null) {
                        fileDiffs.add(FileDiff(currentFilePath, currentChanges.toList()))
                        currentChanges.clear()
                    }
                    currentFilePath = line.substringAfter("Index: ").trim()
                }
                line.startsWith("@@ ") -> {
                    val matchResult = Regex("@@ -\\d+(?:,\\d+)? \\+(\\d+)").find(line)
                    currentLineNumber = matchResult?.groupValues?.get(1)?.toIntOrNull() ?: 1
                }
                line.startsWith("+") && !line.startsWith("+++") -> {
                    currentChanges.add(DiffChange(currentLineNumber, line.substring(1), isAdded = true))
                    currentLineNumber++
                }
                line.startsWith(" ") && !line.startsWith("---") -> {
                    currentLineNumber++
                }
                line.startsWith("-") && !line.startsWith("---") -> {
                    currentLineNumber++
                }
            }
        }

        if (currentFilePath != null && currentChanges.isNotEmpty()) {
            fileDiffs.add(FileDiff(currentFilePath, currentChanges.toList()))
        }

        return fileDiffs
    }
}