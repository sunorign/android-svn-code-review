package com.codereview.core

internal enum class RuleGroup(
    val displayName: String
) {
    JAVA_COMMON("Java 通用规则"),
    ANDROID_COMMON("Android 通用规则")
}

internal abstract class BaseRule {
    abstract val name: String
    abstract val description: String
    abstract val group: RuleGroup
    open val alwaysDisplay: Boolean get() = false

    abstract fun checkDiff(fileDiff: FileDiff, change: DiffChange): List<Finding>
    abstract fun checkFullFile(filePath: String, content: String): List<Finding>

    protected fun isLineComment(line: String): Boolean {
        val trimmed = line.trim()
        return trimmed.startsWith("//") || trimmed.startsWith("/*")
    }

    protected fun removeComments(content: String): String {
        return content.replace(Regex("/\\*[\\s\\S]*?\\*/"), "")
            .replace(Regex("//.*$", RegexOption.MULTILINE), "")
    }

    protected fun isPatternInString(line: String, matchStart: Int, matchEnd: Int): Boolean {
        var inString = false
        var stringQuote: Char? = null
        var escaped = false

        for (i in 0 until line.length) {
            val c = line[i]
            if (escaped) {
                escaped = false
                continue
            }
            if (c == '\\') {
                escaped = true
                continue
            }
            if ((c == '"' || c == '\'') && (i == 0 || line[i - 1] != '\\')) {
                if (!inString) {
                    inString = true
                    stringQuote = c
                } else if (stringQuote == c) {
                    inString = false
                    stringQuote = null
                }
            }
            if (inString && i >= matchStart && i <= matchEnd) {
                return true
            }
        }
        return false
    }
}
