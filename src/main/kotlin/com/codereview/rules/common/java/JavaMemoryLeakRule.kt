package com.codereview.rules.common.java

import com.codereview.core.BaseRule
import com.codereview.core.FileDiff
import com.codereview.core.Finding
import com.codereview.core.DiffChange
import com.codereview.core.Severity

internal class JavaMemoryLeakRule : BaseRule() {
    override val name: String get() = "Java-MemoryLeak"
    override val description: String get() = "检测非静态内部类可能造成的内存泄漏"

    override fun checkDiff(fileDiff: FileDiff, change: DiffChange): List<Finding> {
        val findings = mutableListOf<Finding>()
        if (!change.isAdded) return findings

        val line = change.content
        if (line.contains("class ") && !line.contains("static ") && line.contains("On") && line.contains("Listener")) {
            if (!isLineComment(line)) {
                findings.add(
                    Finding(
                        filePath = fileDiff.filePath,
                        lineNumber = change.lineNumber,
                        ruleName = name,
                        message = "非静态内部类监听器可能造成内存泄漏，建议使用static修饰或弱引用",
                        severity = Severity.WARNING,
                        codeSnippet = line.trim()
                    )
                )
            }
        }
        if (line.contains("new ") && line.contains("Runnable") && !line.contains("static")) {
            if (!isLineComment(line)) {
                findings.add(
                    Finding(
                        filePath = fileDiff.filePath,
                        lineNumber = change.lineNumber,
                        ruleName = name,
                        message = "非静态Runnable可能持有外部Context引用，建议使用static修饰",
                        severity = Severity.WARNING,
                        codeSnippet = line.trim()
                    )
                )
            }
        }
        return findings
    }

    override fun checkFullFile(filePath: String, content: String): List<Finding> {
        val findings = mutableListOf<Finding>()
        val lines = content.lines()
        for ((index, line) in lines.withIndex()) {
            val lineNumber = index + 1
            if (line.contains("class ") && !line.contains("static ") && line.contains("On") && line.contains("Listener")) {
                if (!isLineComment(line)) {
                    findings.add(
                        Finding(
                            filePath = filePath,
                            lineNumber = lineNumber,
                            ruleName = name,
                            message = "非静态内部类监听器可能造成内存泄漏，建议使用static修饰或弱引用",
                            severity = Severity.WARNING,
                            codeSnippet = line.trim()
                        )
                    )
                }
            }
            if (line.contains("new ") && line.contains("Runnable") && !line.contains("static")) {
                if (!isLineComment(line)) {
                    findings.add(
                        Finding(
                            filePath = filePath,
                            lineNumber = lineNumber,
                            ruleName = name,
                            message = "非静态Runnable可能持有外部Context引用，建议使用static修饰",
                            severity = Severity.WARNING,
                            codeSnippet = line.trim()
                        )
                    )
                }
            }
        }
        return findings
    }
}