package com.codereview.ai

data class AiReviewContext(
    val systemPrompt: String,
    val taskPrompt: String,
    val ruleDocs: List<RuleDoc>,
    val codeContent: String
)
