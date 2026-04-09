package com.codereview.ai

data class RuleDoc(
    val name: String,
    val tags: List<String>,
    val content: String,
    val sourcePath: String
)