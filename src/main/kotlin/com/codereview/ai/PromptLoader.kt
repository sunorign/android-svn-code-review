package com.codereview.ai

internal data class LoadedPrompt(
    val content: String,
    val loadedFiles: List<String>
)

internal class PromptLoader {
    fun getCommonFullReviewPrompt(): LoadedPrompt {
        val path = "ai_prompts/common/full-review.md"
        val content = loadPrompt(path)
        return LoadedPrompt(content, listOf(path))
    }

    fun getCommonDiffReviewPrompt(): LoadedPrompt {
        val path = "ai_prompts/common/diff-review.md"
        val content = loadPrompt(path)
        return LoadedPrompt(content, listOf(path))
    }

    private fun loadPrompt(path: String): String {
        val stream = this::class.java.classLoader.getResourceAsStream(path)
            ?: throw IllegalArgumentException("Prompt not found: $path")
        return stream.bufferedReader().use { it.readText() }
    }
}
