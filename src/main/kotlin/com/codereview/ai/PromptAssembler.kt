package com.codereview.ai

internal interface PromptAssembler {
    fun assemble(context: AiReviewContext): String
}

internal class DefaultPromptAssembler : PromptAssembler {

    override fun assemble(context: AiReviewContext): String {
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

            // RuleDocs
            if (context.ruleDocs.isNotEmpty()) {
                appendLine("以下是具体的审查规则，请你按照这些规则进行检查：")
                appendLine()
                for (ruleDoc in context.ruleDocs) {
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
