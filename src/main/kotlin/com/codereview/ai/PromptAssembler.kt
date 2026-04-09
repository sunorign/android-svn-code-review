package com.codereview.ai

// OllamaEmbeddingClient is in the same package


interface PromptAssembler {
    suspend fun assemble(context: AiReviewContext, retrievalMode: RetrievalMode, semanticTopN: Int): String
}

class DefaultPromptAssembler(
    private val queryAnalyzer: QueryAnalyzer = QueryAnalyzer(),
    private val semanticMatcher: SemanticMatcher = SemanticMatcher(),
    private var embeddingClient: EmbeddingClient? = null
) : PromptAssembler {

    fun initEmbeddingClient(config: AiConfig) {
        if (config.retrievalMode == RetrievalMode.SEMANTIC && embeddingClient == null) {
            embeddingClient = when (config.provider) {
                "ollama" -> OllamaEmbeddingClient(config)
                else -> null
            }
        }
    }

    override suspend fun assemble(context: AiReviewContext, retrievalMode: RetrievalMode, semanticTopN: Int): String {
        val filteredRuleDocs = when (retrievalMode) {
            RetrievalMode.NONE -> {
                // No filtering - use all rules
                context.ruleDocs
            }
            RetrievalMode.TAG_MATCHING -> {
                // Keyword-based tag matching (Phase 2)
                if (context.ruleDocs.size > 1) {
                    val keywords = queryAnalyzer.extractKeywords(context.codeContent)
                    queryAnalyzer.filterMatchingRules(context.ruleDocs, keywords)
                } else {
                    context.ruleDocs
                }
            }
            RetrievalMode.SEMANTIC -> {
                // Semantic similarity retrieval with embeddings (Phase 3)
                val client = embeddingClient
                if (client == null || context.ruleDocs.isEmpty()) {
                    // Fallback to tag matching if embedding client not available
                    if (context.ruleDocs.size > 1) {
                        val keywords = queryAnalyzer.extractKeywords(context.codeContent)
                        queryAnalyzer.filterMatchingRules(context.ruleDocs, keywords)
                    } else {
                        context.ruleDocs
                    }
                } else {
                    // Get embedding for input code
                    val embeddingResult = client.embed(context.codeContent)
                    embeddingResult.fold(
                        onSuccess = { queryEmbedding ->
                            semanticMatcher.findSimilarRules(queryEmbedding, context.ruleDocs, semanticTopN)
                        },
                        onFailure = { error ->
                            println("[DefaultPromptAssembler] Failed to get embedding for input code: ${error.message}, falling back to tag matching")
                            // Fallback to tag matching
                            if (context.ruleDocs.size > 1) {
                                val keywords = queryAnalyzer.extractKeywords(context.codeContent)
                                queryAnalyzer.filterMatchingRules(context.ruleDocs, keywords)
                            } else {
                                context.ruleDocs
                            }
                        }
                    )
                }
            }
        }

        return buildString {
            // System Prompt
            appendLine(context.systemPrompt)
            appendLine()
            appendLine("---")
            appendLine()

            // Task Prompt
            appendLine(context.taskPrompt)
            appendLine()
            appendLine("---")
            appendLine()

            // RuleDocs - filtered based on retrieval mode
            if (filteredRuleDocs.isNotEmpty()) {
                appendLine("以下是具体的审查规则，请你按照这些规则进行检查：")
                appendLine()
                for (ruleDoc in filteredRuleDocs) {
                    appendLine("---")
                    appendLine(ruleDoc.content)
                    appendLine("---")
                    appendLine()
                }
                appendLine("---")
                appendLine()
            }

            // Code Input
            appendLine("以下是需要审查的代码：")
            appendLine()
            append(context.codeContent)
        }
    }
}
