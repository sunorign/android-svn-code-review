# AI Prompt 架构升级 - Phase 1 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 AI 提示词模块从单文件加载升级为分层架构，支持 RuleDoc 规则知识体系，为未来 RAG 演进预留空间。

**Architecture:** 按照职责隔离原则，将提示词分为 System / Task / RuleDoc / Code 四层。RuleDoc 支持内置资源文件加载和用户目录自定义加载。PromptAssembler 负责按层次拼接最终提示词。输出协议完全保持不变。

**Tech Stack:** Kotlin + Compose Multiplatform + 反射 + kotlinx.serialization

---

## 文件结构

| 操作 | 文件路径 | 职责 |
|------|----------|------|
| **Create** | `src/main/kotlin/com/codereview/ai/RuleDoc.kt` | RuleDoc 数据类 |
| **Create** | `src/main/kotlin/com/codereview/ai/AiReviewContext.kt` | AiReviewContext 数据类 |
| **Create** | `src/main/kotlin/com/codereview/ai/RuleDocLoader.kt` | RuleDoc 加载器（内置 + 用户自定义） |
| **Create** | `src/main/kotlin/com/codereview/ai/PromptAssembler.kt` | PromptAssembler 接口和默认实现 |
| **Create** | `src/main/resources/ai_rules/system-prompt.md` | System Prompt（固定格式规则） |
| **Create** | `src/main/resources/ai_rules/task-diff.md` | Task Prompt - Diff 模式 |
| **Create** | `src/main/resources/ai_rules/task-global.md` | Task Prompt - Global 模式 |
| **Create** | `src/main/resources/ai_rules/common/java/debug-logging.md` | RuleDoc - Java 调试日志 |
| **Create** | `src/main/resources/ai_rules/common/java/hardcoded-secrets.md` | RuleDoc - 硬编码敏感信息 |
| **Create** | `src/main/resources/ai_rules/common/java/unclosed-resources.md` | RuleDoc - 未关闭资源 |
| **Create** | `src/main/resources/ai_rules/common/java/npe-risk.md` | RuleDoc - 空指针风险 |
| **Create** | `src/main/resources/ai_rules/common/java/memory-leak.md` | RuleDoc - 内存泄漏 |
| **Create** | `src/main/resources/ai_rules/common/android/hardcoded-urls.md` | RuleDoc - 硬编码 URL |
| **Create** | `src/main/resources/ai_rules/common/android/viewholder-pattern.md` | RuleDoc - ViewHolder 模式 |
| **Create** | `src/main/resources/ai_rules/common/android/binary-files.md` | RuleDoc - 二进制文件检查 |
| **Modify** | `src/main/kotlin/com/codereview/gui/MainScreen.kt` | 修改为使用新的 PromptAssembler |
| **Keep** | `src/main/kotlin/com/codereview/ai/PromptLoader.kt` | 保留但不再使用，向后兼容 |
| **Keep** | `src/main/kotlin/com/codereview/ai/AiFindingParser.kt` | 完全不变 |

---

## 任务分解

### Task 1: 创建 RuleDoc 数据类

**Files:**
- Create: `src/main/kotlin/com/codereview/ai/RuleDoc.kt`

- [ ] **Step 1: Create file with data class**

```kotlin
package com.codereview.ai

data class RuleDoc(
    val name: String,
    val tags: List<String>,
    val content: String,
    val sourcePath: String
)
```

- [ ] **Step 2: Compile verification**

Run: `./gradlew.bat compileKotlin`
Expected: Compilation success

- [ ] **Step 3: Commit**

```bash
git add src/main/kotlin/com/codereview/ai/RuleDoc.kt
git commit -m "feat: add RuleDoc data class"
```

---

### Task 2: 创建 AiReviewContext 数据类

**Files:**
- Create: `src/main/kotlin/com/codereview/ai/AiReviewContext.kt`

- [ ] **Step 1: Create file with data class**

```kotlin
package com.codereview.ai

data class AiReviewContext(
    val systemPrompt: String,
    val taskPrompt: String,
    val ruleDocs: List<RuleDoc>,
    val codeContent: String
)
```

- [ ] **Step 2: Compile verification**

Run: `./gradlew.bat compileKotlin`
Expected: Compilation success

- [ ] **Step 3: Commit**

```bash
git add src/main/kotlin/com/codereview/ai/AiReviewContext.kt
git commit -m "feat: add AiReviewContext data class"
```

---

### Task 3: 创建 RuleDocLoader 加载器

**Files:**
- Create: `src/main/kotlin/com/codereview/ai/RuleDocLoader.kt`

- [ ] **Step 1: Create file**

```kotlin
package com.codereview.ai

import java.io.File

internal class RuleDocLoader {

    private val SECTION_PATTERN = Regex("^#\\s*(.+)\\s*$")

    internal fun loadAllRuleDocs(): List<RuleDoc> {
        val result = mutableListOf<RuleDoc>()

        // Load built-in rule docs from resources
        result.addAll(loadBuiltInRuleDocs())

        // Load user custom rule docs from ~/.code-review/rule-docs/
        result.addAll(loadUserRuleDocs())

        // Deduplicate: user rule overrides built-in if name conflict
        return deduplicate(result)
    }

    private fun loadBuiltInRuleDocs(): List<RuleDoc> {
        val result = mutableListOf<RuleDoc>()
        val commonPaths = listOf(
            "ai_rules/common/java",
            "ai_rules/common/android"
        )

        for (basePath in commonPaths) {
            val stream = this::class.java.classLoader.getResource(basePath)
            if (stream != null) {
                val dir = File(stream.toURI())
                if (dir.exists() && dir.isDirectory) {
                    dir.listFiles()?.filter { it.extension == "md" }?.forEach { file ->
                        try {
                            val ruleDoc = parseRuleDoc(file.readText(), file.absolutePath)
                            result.add(ruleDoc)
                        } catch (e: Exception) {
                            println("Warning: Failed to parse built-in RuleDoc ${file.path}: ${e.message}")
                        }
                    }
                }
            }
        }

        return result
    }

    private fun loadUserRuleDocs(): List<RuleDoc> {
        val result = mutableListOf<RuleDoc>()
        val homeDir = System.getProperty("user.home")
        val userDir = File(homeDir, ".code-review/rule-docs")

        if (!userDir.exists()) {
            return emptyList()
        }

        userDir.listFiles()?.filter { it.extension == "md" }?.forEach { file ->
            try {
                val ruleDoc = parseRuleDoc(file.readText(), file.absolutePath)
                result.add(ruleDoc)
            } catch (e: Exception) {
                println("Warning: Failed to parse user RuleDoc ${file.path}: ${e.message}")
            }
        }

        return result
    }

    private fun parseRuleDoc(content: String, sourcePath: String): RuleDoc {
        val lines = content.lines()
        var currentSection: String? = null
        val sections = mutableMapOf<String, StringBuilder>()

        for (line in lines) {
            val trimmed = line.trim()
            val match = SECTION_PATTERN.matchEntire(trimmed)
            if (match != null) {
                currentSection = match.groupValues[1].trim().lowercase()
                sections[currentSection] = StringBuilder()
            } else if (currentSection != null) {
                sections[currentSection]!!.appendLine(line)
            }
        }

        val name = sections["规则名"]?.toString()?.trim()
            ?: sourcePath.substringAfterLast("/").substringBeforeLast(".")
        val tagsStr = sections["标签"]?.toString()?.trim().orEmpty()
        val tags = tagsStr.split(",").map { it.trim() }.filter { it.isNotEmpty() }

        // Combine all remaining content into full document
        val contentBuilder = StringBuilder()
        sections.forEach { (section, builder) ->
            contentBuilder.appendLine("# $section")
            contentBuilder.appendLine(builder.toString().trim())
            contentBuilder.appendLine()
        }

        return RuleDoc(
            name = name,
            tags = tags,
            content = contentBuilder.toString().trim(),
            sourcePath = sourcePath
        )
    }

    private fun deduplicate(ruleDocs: List<RuleDoc>): List<RuleDoc> {
        // Last occurrence (user) wins
        return ruleDocs.reversed().distinctBy { it.name }.reversed()
    }
}
```

- [ ] **Step 2: Compile verification**

Run: `./gradlew.bat compileKotlin`
Expected: Compilation success

- [ ] **Step 3: Commit**

```bash
git add src/main/kotlin/com/codereview/ai/RuleDocLoader.kt
git commit -m "feat: add RuleDocLoader with built-in and user loading"
```

---

### Task 4: 创建 PromptAssembler

**Files:**
- Create: `src/main/kotlin/com/codereview/ai/PromptAssembler.kt`

- [ ] **Step 1: Create file**

```kotlin
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
```

- [ ] **Step 2: Compile verification**

Run: `./gradlew.bat compileKotlin`
Expected: Compilation success

- [ ] **Step 3: Commit**

```bash
git add src/main/kotlin/com/codereview/ai/PromptAssembler.kt
git commit -m "feat: add PromptAssembler interface and default implementation"
```

---

### Task 5: 创建 System Prompt 和 Task Prompt 文件

**Files:**
- Create: `src/main/resources/ai_rules/system-prompt.md`
- Create: `src/main/resources/ai_rules/task-diff.md`
- Create: `src/main/resources/ai_rules/task-global.md`

- [ ] **Step 1: Create system-prompt.md**

```markdown
你是一个专业的 Android 代码审查 AI。

# 输出格式要求

1. 先分析代码，说明你的思考过程
2. 最后将所有问题放在 `<findings>` 和 `</findings>` 标签之间
3. **严格遵守：** 每个问题单独用 `<question>` 和 `</question>` 包裹

**格式：**
```
<question>
file_path=包名.类名&line_start=起始行&line_end=结束行&issue_type=问题类型&severity=BLOCK&message=问题描述&suggestion=修改建议&always_display=true
</question>
```

**severity 取值：**
- `BLOCK` - 严重问题，需要修复（会导致 CI 检查失败）
- `WARNING` - 一般问题，建议修复
- `PASS` - 检查通过，不涉及问题

**必须遵守的规则：**
- 使用点分隔包名：`com.example.Main`，**禁止**斜杠 `/` 或反斜杠 `\`
- **`&` 字符只能用于参数之间的分隔符，你的 `message` 和 `suggestion` 内容中绝对不能出现 `&` 字符**。如果需要表示 `和`，请直接用汉字 `和` 代替。任何情况下都不允许内容中包含 `&`。
- **特别禁止：**不要输出 HTML 实体编码如 `&quot;` `&amp;` `&lt;` `&gt;`，这些都包含 `&` 字符，会导致解析错误。直接输出原文即可。
- **key=value 格式中，key 和 value 内容禁止包含 `<` 或 `>` 字符**
- `message` 和 `suggestion` **内容可以**换行，解析器能正确处理
- 每个问题必须完整包裹在 `<question>...</question>` 中
- 所有问题写完后，在 `<findings>` 最后一行单独写：`total=问题数量`
- always_display=[true|false] - 可选，是否固定显示该检查项，默认为 false。如果为 true，即使本次未发现问题也会在报告中保留展示。

**正确示例：**
```
<findings>
<question>
file_path=com.example.Main&line_start=10&line_end=15&issue_type=BUG&severity=BLOCK&message=BitmapFactory.decodeResource 可能返回 null&suggestion=if (bitmap != null) { BitmapUtils.saveBmp(bitmap, mReceipeName); }
</question>
<question>
file_path=com.example.utils.Utils&line_start=29&line_end=35&issue_type=PERFORMANCE&severity=WARNING&message=循环创建对象不必要&suggestion=提取到循环外
</question>
total=2
</findings>
```

**错误示例（禁止）：**
```
<question>
file_path=com.example.Main
&line_start=10  ❌ & 换行放开头，解析失败
```

```
<question>
file_path=com.example.Main&line_start=10&line_end=15&message=a 和 b&suggestion=... ✅ 正确，用汉字"和"
file_path=com.example.Main&line_start=10&line_end=15&message=a & b&suggestion=... ❌ 错误，message 中包含 &，会导致解析错误
</question>
```

- 如果没有发现问题，输出：`<findings>total=0</findings>`
- 格式错误无法解析，请严格遵守以上规则
```

- [ ] **Step 2: Create task-diff.md**

```markdown
当前是 Diff 增量代码审查。

你需要仔细分析本次变更的代码内容，重点关注改动部分，找出变更引入的潜在 bug、安全问题、不规范写法和性能问题。

只分析本次修改的代码，无需分析整个文件中未改动的部分。
```

- [ ] **Step 3: Create task-global.md**

```markdown
当前是完整文件代码审查。

你需要仔细分析整个 Android 源文件的完整内容，找出潜在的 bug、安全问题、不规范写法、性能问题和不好的实践。
```

- [ ] **Step 4: Commit**

```bash
git add src/main/resources/ai_rules/system-prompt.md
git add src/main/resources/ai_rules/task-diff.md
git add src/main/resources/ai_rules/task-global.md
git commit -m "feat: add system prompt and task prompts for diff/global"
```

---

### Task 6: 创建内置 RuleDoc 文件（Java 通用规则）

**Files:**
- Create: `src/main/resources/ai_rules/common/java/debug-logging.md`
- Create: `src/main/resources/ai_rules/common/java/hardcoded-secrets.md`
- Create: `src/main/resources/ai_rules/common/java/unclosed-resources.md`
- Create: `src/main/resources/ai_rules/common/java/npe-risk.md`
- Create: `src/main/resources/ai_rules/common/java/memory-leak.md`

- [ ] **Step 1: Create debug-logging.md**

```markdown
# 规则名
调试日志检查

# 标签
debug, log, logging, java

# 描述
检查代码中残留的调试日志代码，这些代码应该在发布前移除。

需要检查的模式包括：
- System.out.println
- Log.d / Log.v（调试级别日志）

Log.i / Log.w / Log.e 是正式日志，不需要报告。

发现调试日志报告 BLOCK 级别问题，必须移除。
```

- [ ] **Step 2: Create hardcoded-secrets.md**

```markdown
# 规则名
硬编码敏感信息

# 标签
security, secret, password, key, hardcode, java

# 描述
检测代码中硬编码的密码、密钥、API Key、令牌等敏感信息。

这些敏感信息硬编码在代码中会导致安全风险，应该从配置文件或环境变量读取。

发现硬编码敏感信息报告 BLOCK 级别问题。
```

- [ ] **Step 3: Create unclosed-resources.md**

```markdown
# 规则名
未关闭资源检查

# 标签
resource, leak, io, cursor, stream, connection, java

# 描述
检查代码中 Cursor、InputStream、OutputStream、Connection 等资源是否正确关闭。

重点关注：
- 打开资源后，在所有退出路径是否都有 close() 调用
- 是否使用 try-with-resources 语法自动关闭
- 异常处理分支是否遗漏关闭

发现未关闭资源报告 WARNING 级别问题。
```

- [ ] **Step 4: Create npe-risk.md**

```markdown
# 规则名
空指针风险检查

# 标签
null, npe, pointer, kotlin, java

# 描述
识别代码中可能出现空指针异常的场景：
- 多级可空链式调用：obj?.let?.map?.apply
- !! 非空断言的潜在风险
- 可空类型变量未判空直接使用
- 平台类型从 Java 来，Kotlin 当作非空处理

分析是否存在肯定会触发 NPE 的代码，如果有报告 BLOCK，有潜在风险报告 WARNING。
```

- [ ] **Step 5: Create memory-leak.md**

```markdown
# 规则名
内存泄漏风险

# 标签
memory, leak, inner-class, android, java

# 描述
检测可能导致内存泄漏的代码：
- 非静态内部类持有外部 Activity/Context 引用
- 静态变量持有 Activity 实例
- Handler  post 延迟消息持有 Context
- 未注销的监听器

发现潜在内存泄漏报告 WARNING 级别问题。
```

- [ ] **Step 6: Commit**

```bash
git add src/main/resources/ai_rules/common/java/*.md
git commit -m "feat: add built-in RuleDocs for Java common rules"
```

---

### Task 7: 创建内置 RuleDoc 文件（Android 通用规则）

**Files:**
- Create: `src/main/resources/ai_rules/common/android/hardcoded-urls.md`
- Create: `src/main/resources/ai_rules/common/android/viewholder-pattern.md`
- Create: `src/main/resources/ai_rules/common/android/binary-files.md`

- [ ] **Step 1: Create hardcoded-urls.md**

```markdown
# 规则名
硬编码 IP/URL

# 标签
url, ip, hardcode, network, android

# 描述
检查代码中硬编码的 IP 地址或 URL。

服务地址应该配置在远端或配置文件中，不应该硬编码在代码中，避免修改需要重新发布。

发现硬编码 URL/IP 报告 WARNING 级别问题。
```

- [ ] **Step 2: Create viewholder-pattern.md**

```markdown
# 规则名
ViewHolder 模式检查

# 标签
ui, listview, recyclerview, viewholder, pattern, android

# 描述
检查 ListView/RecyclerView 中是否正确使用 ViewHolder 模式。

错误做法：getView/onBindViewHolder 中每次都调用 findViewById
正确做法：使用 ViewHolder 缓存 findViewById 结果

未正确使用 ViewHolder 模式报告 WARNING 级别问题，影响滑动性能。
```

- [ ] **Step 3: Create binary-files.md**

```markdown
# 规则名
二进制文件检查

# 标签
binary, apk, dex, aar, so, file, android

# 描述
检查代码仓库中是否提交了 .apk / .dex / .aar / .so 等二进制文件。

这些文件不应该提交到代码仓库，会导致仓库体积膨胀。

发现二进制文件报告 BLOCK 级别问题，必须移除。
```

- [ ] **Step 4: Commit**

```bash
git add src/main/resources/ai_rules/common/android/*.md
git commit -m "feat: add built-in RuleDocs for Android common rules"
```

---

### Task 8: 修改 MainScreen 使用新的 PromptAssembler

**Files:**
- Modify: `src/main/kotlin/com/codereview/gui/MainScreen.kt`

- [ ] **Step 1: Add imports**

Add to imports:
```kotlin
import com.codereview.ai.RuleDocLoader
import com.codereview.ai.AiReviewContext
import com.codereview.ai.DefaultPromptAssembler
```

- [ ] **Step 2: Modify the prompt loading section in `runReview`**

Around line 300-310:

**Replace:**
```kotlin
val aiClient = AiClientFactory.create(aiConfig)
val promptLoader = PromptLoader()
val loadedPrompt = promptLoader.getCommonFullReviewPrompt()
prompt = loadedPrompt.content
promptFiles = loadedPrompt.loadedFiles

// Take first 10 files for AI review
val codeContent = files.take(10).joinToString("\n\n---\n\n") { file ->
```

**With:**
```kotlin
val aiClient = AiClientFactory.create(aiConfig)

// New layered prompt assembly
val ruleDocLoader = RuleDocLoader()
val allRuleDocs = ruleDocLoader.loadAllRuleDocs()

val systemPrompt = this::class.java.classLoader.getResourceAsStream("ai_rules/system-prompt.md")
    ?.bufferedReader()?.use { it.readText() }
    ?: throw IllegalStateException("system-prompt.md not found in resources")

val taskPrompt = if (scanSettings.scanMode == ScanMode.FULL) {
    this::class.java.classLoader.getResourceAsStream("ai_rules/task-global.md")
        ?.bufferedReader()?.use { it.readText() }
} else {
    this::class.java.classLoader.getResourceAsStream("ai_rules/task-diff.md")
        ?.bufferedReader()?.use { it.readText() }
} ?: throw IllegalStateException("task prompt not found in resources")

val promptAssembler = DefaultPromptAssembler()

// Take first 10 files for AI review
val codeContent = files.take(10).joinToString("\n\n---\n\n") { file ->
```

Then **replace:**
```kotlin
aiResponse = aiClient.review(prompt, codeContent)
```

**With:**
```kotlin
val context = AiReviewContext(
    systemPrompt = systemPrompt,
    taskPrompt = taskPrompt,
    ruleDocs = allRuleDocs,
    codeContent = codeContent
)
val assembledPrompt = promptAssembler.assemble(context)
prompt = assembledPrompt
promptFiles = allRuleDocs.map { it.sourcePath }

aiResponse = aiClient.review(assembledPrompt)
```

- [ ] **Step 3: Compile verification**

Run: `./gradlew.bat compileKotlin`
Expected: Compilation success

- [ ] **Step 4: Fix any compilation errors**

If there are errors, fix them and re-verify.

- [ ] **Step 5: Commit**

```bash
git add src/main/kotlin/com/codereview/gui/MainScreen.kt
git commit -m "refactor: use new PromptAssembler with layered architecture"
```

---

### Task 9: 构建验证和测试

**Files:**
- None, just build and verify

- [ ] **Step 1: Full clean build**

Run: `./gradlew.bat clean build`
Expected: Build completes successfully

- [ ] **Step 2: Run GUI to verify it starts**

Run: `./gradlew.bat run`
Expected: GUI window opens, no crash

- [ ] **Step 3: Commit any final fixes if needed**

If fixes were needed:
```bash
git add ...
git commit -m "fix: build fixes"
```

---

## 自审查

- ✅ 规格覆盖：所有 Phase 1 需求都有对应任务
- ✅ 无占位符：所有文件路径和代码都完整提供
- ✅ 类型一致：所有数据类和接口名称一致
- ✅ 可增量验证：每个任务完成后都能编译通过，Task 9 整体验证
- ✅ 输出协议不变：AiFindingParser 完全不修改，保持兼容

---

