package com.codereview.core

import com.codereview.core.ScanMode
import com.codereview.core.ScanSettings
import java.io.File

private val DEFAULT_IGNORE_PATTERNS = listOf(
    "build/",
    "*/build/",
    "app/build/",
    "generated/",
    "*/generated/",
    ".git/",
    ".svn/"
)

private val binaryExtensions = setOf(".apk", ".dex", ".jar", ".class", ".so", ".png", ".jpg", ".jpeg", ".gif", ".ico")

internal class Scanner {
    fun shouldIgnore(file: File, baseDir: File): Boolean {
        val relativePath = baseDir.toPath().relativize(file.toPath()).toString().replace('\\', '/')

        for (pattern in DEFAULT_IGNORE_PATTERNS) {
            if (matchPattern(relativePath, pattern)) {
                return true
            }
        }

        // Ignore binary files by extension
        val ext = file.extension.lowercase()
        if (ext in binaryExtensions) {
            return true
        }

        return false
    }

    private fun matchPattern(relativePath: String, pattern: String): Boolean {
        return when {
            pattern.startsWith("*/") -> {
                val suffix = pattern.substring(2)
                relativePath.endsWith(suffix) || relativePath.contains("/$suffix")
            }
            else -> {
                relativePath.startsWith(pattern) || relativePath.contains("/$pattern")
            }
        }
    }

    fun scanProject(baseDir: File): List<File> {
        val result = mutableListOf<File>()
        fun scan(dir: File) {
            dir.listFiles()?.forEach { file ->
                if (file.isDirectory) {
                    if (!shouldIgnore(file, baseDir)) {
                        scan(file)
                    }
                } else {
                    if (!shouldIgnore(file, baseDir)) {
                        val ext = file.extension.lowercase()
                        if (ext in setOf("java", "kt", "kotlin")) {
                            result.add(file)
                        }
                    }
                }
            }
        }
        scan(baseDir)
        return result
    }

    fun scan(baseDir: File, settings: ScanSettings): List<File> {
        return when (settings.scanMode) {
            ScanMode.FULL -> {
                scanProject(baseDir)
            }
            ScanMode.SVN_DIFF, ScanMode.GIT_DIFF -> {
                val diffScanner = DiffScanner()
                val changedFiles = diffScanner.getChangedFiles(baseDir, settings.scanMode)
                // 对变更文件应用现有的 ignore 规则过滤
                changedFiles.filter { file ->
                    val ext = file.extension.lowercase()
                    ext in setOf("java", "kt", "kotlin") && !shouldIgnore(file, baseDir)
                }
            }
        }
    }
}