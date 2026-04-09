package com.codereview.ai

import kotlinx.serialization.Serializable

/**
 * Metadata for an AI finding - stores additional information about where it came from.
 */
@Serializable
data class FindingMetadata(
    /**
     * Name of the RuleDoc that this finding corresponds to.
     */
    val ruleName: String? = null,
    /**
     * Relevance score from matching (0.0 - 1.0).
     */
    val relevance: Double? = null,
    /**
     * Tags that matched for this finding.
     */
    val tags: List<String> = emptyList()
)

/**
 * Represents a single issue/finding found by AI code review.
 */
@Serializable
data class AiFinding(
    val priority: String,      // 严重/一般/轻微
    val issueType: String,     // 问题分类
    val location: String,      // 文件路径:行号
    val description: String,   // 详细描述
    val suggestion: String,    // 修复建议
    val alwaysDisplay: Boolean = false,
    /**
     * Additional metadata about this finding (Phase 2+).
     */
    val metadata: FindingMetadata = FindingMetadata()
)
