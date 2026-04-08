package com.codereview.core

import java.io.File

internal class DiffScanner {

    /**
     * 获取变更文件列表
     * @param baseDir 项目根目录
     * @param scanMode 扫描模式 (SVN_DIFF 或 GIT_DIFF)
     * @return 变更文件的绝对路径列表，如果出错返回空列表
     */
    fun getChangedFiles(baseDir: File, scanMode: ScanMode): List<File> {
        require(scanMode == ScanMode.SVN_DIFF || scanMode == ScanMode.GIT_DIFF) {
            "Unsupported scanMode: $scanMode"
        }

        val diffOutput = runDiffCommand(baseDir, scanMode) ?: return emptyList()
        return parseChangedFiles(diffOutput, baseDir, scanMode)
    }

    private fun runDiffCommand(baseDir: File, scanMode: ScanMode): String? {
        val command = when (scanMode) {
            ScanMode.SVN_DIFF -> listOf("svn", "diff")
            ScanMode.GIT_DIFF -> listOf("git", "diff", "--name-only")
            else -> null
        }

        return try {
            val process = ProcessBuilder(command)
                .directory(baseDir)
                .redirectErrorStream(true)
                .start()

            val output = process.inputStream.bufferedReader().readText()
            val exitCode = process.waitFor()

            // svn diff 返回 0 表示无差异，非 0 可能有差异也可能出错
            // git diff --name-only 返回 0 无论有无差异
            output
        } catch (e: Exception) {
            // 命令执行失败（svn/git 未安装，不是工作副本等）
            null
        }
    }

    private fun parseChangedFiles(output: String, baseDir: File, scanMode: ScanMode): List<File> {
        val changedFiles = mutableListOf<File>()

        when (scanMode) {
            ScanMode.SVN_DIFF -> {
                // SVN diff 格式: Index: path/to/file.java
                val indexPattern = Regex("^Index: (.+)$", RegexOption.MULTILINE)
                indexPattern.findAll(output).forEach { match ->
                    val path = match.groupValues[1].trim()
                    val file = File(baseDir, path)
                    if (file.exists() && file.isFile) {
                        changedFiles.add(file)
                    }
                }
            }
            ScanMode.GIT_DIFF -> {
                // git diff --name-only 格式: 每行一个路径
                output.lines().forEach { line ->
                    val path = line.trim()
                    if (path.isNotEmpty()) {
                        val file = File(baseDir, path)
                        if (file.exists() && file.isFile) {
                            changedFiles.add(file)
                        }
                    }
                }
            }
            else -> {}
        }

        return changedFiles.distinct()
    }
}
