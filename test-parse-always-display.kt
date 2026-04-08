#!/usr/bin/env kotlinc -script

import com.codereview.ai.AiFindingParser

fun main() {
    println("Testing always_display parameter parsing...")
    println("==============================================")

    // Test 1: No always_display parameter (should default to false)
    val test1 = """
<findings>
    <question>
        file_path=MainActivity.kt
        &line_start=42
        &line_end=42
        &issue_type=内存泄漏
        &severity=严重
        &message=静态引用导致Activity内存泄漏
        &suggestion=使用applicationContext替代ActivityContext
    </question>
</findings>
""".trimIndent()

    println("\nTest 1 - No always_display parameter:")
    val result1 = AiFindingParser.parseFindings(test1)
    println("  Findings: ${result1.findings.size}")
    result1.findings.forEachIndexed { i, finding ->
        println("  Finding $i: alwaysDisplay=${finding.alwaysDisplay}")
        println("  All fields: $finding")
    }
    println("  Debug log: ${result1.debugLog}")

    // Test 2: always_display=true (should parse as true)
    val test2 = """
<findings>
    <question>
        file_path=MainActivity.kt
        &line_start=42
        &line_end=42
        &issue_type=内存泄漏
        &severity=严重
        &message=静态引用导致Activity内存泄漏
        &suggestion=使用applicationContext替代ActivityContext
        &always_display=true
    </question>
</findings>
""".trimIndent()

    println("\nTest 2 - always_display=true:")
    val result2 = AiFindingParser.parseFindings(test2)
    println("  Findings: ${result2.findings.size}")
    result2.findings.forEachIndexed { i, finding ->
        println("  Finding $i: alwaysDisplay=${finding.alwaysDisplay}")
        println("  All fields: $finding")
    }
    println("  Debug log: ${result2.debugLog}")

    // Test 3: always_display=false (should parse as false)
    val test3 = """
<findings>
    <question>
        file_path=MainActivity.kt
        &line_start=42
        &line_end=42
        &issue_type=内存泄漏
        &severity=严重
        &message=静态引用导致Activity内存泄漏
        &suggestion=使用applicationContext替代ActivityContext
        &always_display=false
    </question>
</findings>
""".trimIndent()

    println("\nTest 3 - always_display=false:")
    val result3 = AiFindingParser.parseFindings(test3)
    println("  Findings: ${result3.findings.size}")
    result3.findings.forEachIndexed { i, finding ->
        println("  Finding $i: alwaysDisplay=${finding.alwaysDisplay}")
        println("  All fields: $finding")
    }
    println("  Debug log: ${result3.debugLog}")

    // Test 4: always_display with invalid value (should default to false)
    val test4 = """
<findings>
    <question>
        file_path=MainActivity.kt
        &line_start=42
        &line_end=42
        &issue_type=内存泄漏
        &severity=严重
        &message=静态引用导致Activity内存泄漏
        &suggestion=使用applicationContext替代ActivityContext
        &always_display=invalid
    </question>
</findings>
""".trimIndent()

    println("\nTest 4 - always_display=invalid:")
    val result4 = AiFindingParser.parseFindings(test4)
    println("  Findings: ${result4.findings.size}")
    result4.findings.forEachIndexed { i, finding ->
        println("  Finding $i: alwaysDisplay=${finding.alwaysDisplay}")
        println("  All fields: $finding")
    }
    println("  Debug log: ${result4.debugLog}")

    println("\n==============================================")
    println("All tests completed successfully!")
}
