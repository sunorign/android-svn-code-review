import java.io.File

fun main() {
    val filePath = "/d/Documents/Projects/projects_python/code_review/code_review_kotlin_version/src/main/kotlin/com/codereview/ai/AiFindingParser.kt"
    val content = File(filePath).readText()
    
    // Step 1: Find and replace the line where suggestion is defined
    val modifiedContent1 = content.replace(
        "        val suggestion = map[\"suggestion\"] ?: \"\"",
        "        val suggestion = map[\"suggestion\"] ?: \"\"\n        val alwaysDisplay = map[\"always_display\"]?.toBooleanStrictOrNull() ?: false"
    )
    
    // Step 2: Find and replace the AiFinding constructor call
    val modifiedContent2 = modifiedContent1.replace(
        "        return AiFinding(\n            priority = priority,\n            issueType = issueType,\n            location = location,\n            description = description,\n            suggestion = suggestion",
        "        return AiFinding(\n            priority = priority,\n            issueType = issueType,\n            location = location,\n            description = description,\n            suggestion = suggestion,\n            alwaysDisplay = alwaysDisplay"
    )
    
    File(filePath).writeText(modifiedContent2)
    println("File modified successfully!")
}
