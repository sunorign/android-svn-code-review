import com.codereview.report.ReviewResult
import com.codereview.core.Finding
import com.codereview.ai.AiFinding

fun main() {
    // Create a test ReviewResult with AI error
    val testResult = ReviewResult(
        localFindings = emptyList(),
        aiFindings = emptyList(),
        projectName = "test-project",
        scannedFiles = 10,
        durationMs = 1000,
        aiEnabled = true,
        aiProvider = "openrouter",
        aiModel = "minimax/minimax-m2.5:free",
        aiRawResponse = "{\"error\": \"Cannot read Json element because of unexpected end of the input at path: $\"}",
        aiErrorMessage = "Cannot read Json element because of unexpected end of the input at path: $",
        aiDebugInfo = "AI Provider: openrouter\nAI Model: minimax/minimax-m2.5:free\nAPI URL: https://openrouter.ai/api/v1/chat/completions\nResponse Status: Failure\nError: Cannot read Json element because of unexpected end of the input at path: $"
    )

    // Print the structure to verify our changes
    println("ReviewResult with AI error:")
    println("aiErrorMessage: ${testResult.aiErrorMessage}")
    println("aiRawResponse: ${testResult.aiRawResponse}")
    println("\nDebug info:")
    println(testResult.aiDebugInfo)
}
