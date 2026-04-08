import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

// Copy of the data class
@Serializable
data class AiFinding(
    val priority: String,
    val issueType: String,
    val location: String,
    val description: String,
    val suggestion: String
)

// Test the regex parsing
fun parseFindingsFromMarkdown(text: String): List<AiFinding> {
    val findings = mutableListOf<AiFinding>()

    // First try to extract JSON from markdown code blocks
    val jsonBlockRegex = "```json\\n([\\s\\S]*?)\\n```".toRegex()
    val jsonMatch = jsonBlockRegex.find(text)

    if (jsonMatch != null) {
        val jsonContent = jsonMatch.groupValues[1]
        return try {
            Json.decodeFromString<List<AiFinding>>(jsonContent)
        } catch (e: Exception) {
            // If list parsing fails, try to parse a single finding object
            try {
                listOf(Json.decodeFromString<AiFinding>(jsonContent))
            } catch (ex: Exception) {
                emptyList()
            }
        }
    }

    // Fallback to table parsing
    return emptyList()
}

fun main() {
    // Test 1: Single finding in code block
    val test1 = """
```json
{
    "priority": "严重",
    "issueType": "内存泄漏",
    "location": "MainActivity.kt:42",
    "description": "静态引用导致Activity内存泄漏",
    "suggestion": "使用applicationContext替代ActivityContext"
}
```
"""

    // Test 2: Multiple findings in code block
    val test2 = """
```json
[
{
    "priority": "严重",
    "issueType": "内存泄漏",
    "location": "MainActivity.kt:42",
    "description": "静态引用导致Activity内存泄漏",
    "suggestion": "使用applicationContext替代ActivityContext"
},
{
    "priority": "一般",
    "issueType": "性能问题",
    "location": "Utils.kt:123",
    "description": "频繁创建字符串对象",
    "suggestion": "使用StringBuilder代替+操作"
}
]
```
"""

    // Test 3: No code block (fallback)
    val test3 = """
|优先级|问题类型|位置|描述|建议|
|----|----|----|----|----|
|严重|内存泄漏|MainActivity.kt:42|静态引用导致Activity内存泄漏|使用applicationContext替代ActivityContext|
"""

    val result1 = parseFindingsFromMarkdown(test1)
    println("Test 1 results: $result1")

    val result2 = parseFindingsFromMarkdown(test2)
    println("Test 2 results: $result2")

    val result3 = parseFindingsFromMarkdown(test3)
    println("Test 3 results: $result3")
}