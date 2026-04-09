package com.codereview.ai

import kotlinx.serialization.Transient

data class RuleDoc(
    val name: String,
    val tags: List<String>,
    val content: String,
    val sourcePath: String,
    @Transient
    var embedding: FloatArray? = null
)