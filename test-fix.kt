import com.codereview.ai.AiResponse
import com.codereview.ai.AiFinding

// This is a simple test to verify our cleanup logic works correctly
fun main() {
    // Simulate a raw JSON response with lots of whitespace and newlines
    val messyRawResponse = """
        {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "Here is some markdown response\n\n| Priority | Type | Location | Description | Suggestion |\n|----------|------|----------|-------------|-------------|\n| 严重 | Bug | MainActivity.kt:10 | Memory leak | Use WeakReference |"
                }
            ],
            "model": "claude-3-sonnet-20240229",
            "stop_reason": "end_turn",
            "stop_sequence": null,
            "usage": {
                "input_tokens": 100,
                "output_tokens": 200
            }
        }
    """.trimIndent()

    // Test our cleanup logic
    val cleanedRawResponse = messyRawResponse.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()

    println("Original raw response length: ${messyRawResponse.length}")
    println("Cleaned raw response length: ${cleanedRawResponse.length}")
    println("\nOriginal raw response:")
    println(messyRawResponse.substring(0, 200) + "...")
    println("\nCleaned raw response:")
    println(cleanedRawResponse.substring(0, 200) + "...")

    // Test that we can create an AiResponse with cleaned raw response
    val finding = AiFinding("严重", "Bug", "MainActivity.kt:10", "Memory leak", "Use WeakReference")
    val response = AiResponse(success = true, findings = listOf(finding), rawResponse = cleanedRawResponse)

    println("\nAiResponse created successfully:")
    println("Success: ${response.success}")
    println("Findings count: ${response.findings.size}")
    println("Raw response length: ${response.rawResponse?.length}")
}
