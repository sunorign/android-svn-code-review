package com.codereview.ai

/**
 * Semantic similarity matcher using embedding vectors.
 * Uses cosine similarity to find most relevant rules for input code.
 */
class SemanticMatcher {

    /**
     * Precompute embeddings for all rule docs and cache them in RuleDoc objects.
     * This should be called once at application startup after loading rules.
     */
    suspend fun precomputeEmbeddings(
        ruleDocs: List<RuleDoc>,
        embeddingClient: EmbeddingClient
    ) {
        for (ruleDoc in ruleDocs) {
            if (ruleDoc.embedding == null) {
                val result = embeddingClient.embed(ruleDoc.content)
                result.fold(
                    onSuccess = { embedding ->
                        ruleDoc.embedding = embedding
                    },
                    onFailure = { error ->
                        // Leave embedding null - this rule will be skipped in matching
                        println("[SemanticMatcher] Failed to precompute embedding for ${ruleDoc.name}: ${error.message}")
                    }
                )
            }
        }
    }

    /**
     * Find the top-N most similar rules to the query embedding.
     * @param queryEmbedding Embedding of the input code
     * @param ruleDocs All available rule documents with precomputed embeddings
     * @param topN Number of most similar rules to return
     * @return List of most similar rules sorted by similarity (descending)
     */
    fun findSimilarRules(
        queryEmbedding: FloatArray,
        ruleDocs: List<RuleDoc>,
        topN: Int
    ): List<RuleDoc> {
        // Filter out rules that don't have embeddings (precomputation failed)
        val rulesWithEmbeddings = ruleDocs.filter { it.embedding != null }

        if (rulesWithEmbeddings.isEmpty()) {
            return ruleDocs // Fallback to all rules if no embeddings available
        }

        // Calculate cosine similarity for each rule
        val scored = rulesWithEmbeddings.map { rule ->
            val similarity = cosineSimilarity(queryEmbedding, rule.embedding!!)
            rule to similarity
        }

        // Sort by similarity descending and take top-N
        return scored
            .sortedByDescending { it.second }
            .take(topN)
            .map { it.first }
    }

    /**
     * Calculate cosine similarity between two vectors.
     * cos(a, b) = (a · b) / (||a|| * ||b||)
     * @return Similarity in range [-1, 1], higher = more similar
     */
    private fun cosineSimilarity(a: FloatArray, b: FloatArray): Double {
        require(a.size == b.size) { "Vectors must have same dimension" }

        var dotProduct = 0.0
        var normA = 0.0
        var normB = 0.0

        for (i in a.indices) {
            val ai = a[i]
            val bi = b[i]
            dotProduct += (ai * bi).toDouble()
            normA += (ai * ai).toDouble()
            normB += (bi * bi).toDouble()
        }

        if (normA == 0.0 || normB == 0.0) {
            return 0.0
        }

        return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB))
    }
}
