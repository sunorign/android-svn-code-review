import java.io.File

fun main() {
    val file = File("src/main/kotlin/com/codereview/ai/AiFindingParser.kt")
    var content = file.readText()

    // Add the alwaysDisplay variable declaration
    val oldSuggestion = "        val suggestion = map[\"suggestion\"] ?: \"\""
    val newSuggestion = """        val suggestion = map["suggestion"] ?: ""
        val alwaysDisplay = map["always_display"]?.toBooleanStrictOrNull() ?: false"""
    content = content.replace(oldSuggestion, newSuggestion)

    // Add the parameter to the AiFinding constructor
    val oldConstructor = """        return AiFinding(
            priority = priority,
            issueType = issueType,
            location = location,
            description = description,
            suggestion = suggestion
        )"""
    val newConstructor = """        return AiFinding(
            priority = priority,
            issueType = issueType,
            location = location,
            description = description,
            suggestion = suggestion,
            alwaysDisplay = alwaysDisplay
        )"""
    content = content.replace(oldConstructor, newConstructor)

    file.writeText(content)
    println("File modified successfully!")
}
