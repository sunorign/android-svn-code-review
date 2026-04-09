# AI Prompt 架构升级 - Phase 1 设计规格

## 概述

将 AI 审查模块从"单一提示词文件加载"升级为 **Prompt 分层 + RuleDoc 知识体系**架构，为未来 RAG 演进预留空间。

本文档是 **Phase 1** 的设计规格，只实现基础架构，每个阶段独立可验证。

## 背景

当前状态：
- AI 提示词按 `full-review.md` / `diff-review.md` 单文件加载
- 指令、格式规则、审查规则混杂在同一个文件中
- 未来添加规则会导致提示词体积膨胀，增加冲突和幻觉风险

改造目标（Phase 1）：
- 按职责分层：System / Task / RuleDoc / Code
- RuleDoc 独立存储，支持内置 + 用户自定义
- 保持输出协议完全不变，不影响现有解析逻辑
- 所有功能可验证，完成后即可发布使用

## 架构设计

### 分层架构

| 层级 | 职责 | 变化特性 |
|------|------|----------|
| **System Prompt** | AI 身份定义 + 输出格式规则 | 固定不变 |
| **Task Prompt** | 任务行为指导 | 按 Diff / Global 模式变化 |
| **RuleDoc** | 具体审查规则知识 | 多个规则文档，Phase 1 全部注入 |
| **Code Input** | 待审查代码内容 | 每次扫描动态变化 |

### 新流程图

```
代码输入
  ↓
加载 System Prompt (固定)
  ↓
加载 Task Prompt (按模式)
  ↓
加载所有 RuleDoc (内置 + 用户自定义)
  ↓
PromptAssembler 组装
  ↓
Ai Provider 调用
  ↓
Parser 解析 (不变)
  ↓
Report 生成 (不变)
```

## 数据结构

### RuleDoc

```kotlin
data class RuleDoc(
    val name: String,           // 规则名
    val tags: List<String>,     // 标签（Phase 2 用于检索，Phase 1 仅存储）
    val content: String,        // 规则文档内容（Markdown）
    val sourcePath: String      // 源文件路径（调试用）
)
```

### AiReviewContext

```kotlin
data class AiReviewContext(
    val systemPrompt: String,
    val taskPrompt: String,
    val ruleDocs: List<RuleDoc>,
    val codeContent: String
)
```

### PromptAssembler 接口

```kotlin
interface PromptAssembler {
    fun assemble(context: AiReviewContext): String
}
```

默认实现 `DefaultPromptAssembler` 按固定顺序拼接。

## RuleDoc 存储与加载

### 文件位置

| 位置 | 类型 | 说明 |
|------|------|------|
| `src/main/resources/ai_rules/common/java/` | 内置 | Java 通用规则 |
| `src/main/resources/ai_rules/common/android/` | 内置 | Android 通用规则 |
| `~/.code-review/rule-docs/` | 用户自定义 | 用户添加的规则，不重新编译即可生效 |

### RuleDoc 文件格式

每个规则一个 `.md` 文件，示例：

```markdown
# 规则名
空指针风险检查

# 标签
null, pointer, npe, java

# 场景
多级链式调用，返回值未判空，非空断言滥用

# 描述
识别代码中可能出现空指针异常的场景：
- obj?.let?.map?.apply 链式连续调用
- !! 非空断言的潜在风险
- 可空类型变量未判空直接使用

# 检查要点
重点关注返回值声明为可空但调用时未检查的情况。
如果发现肯定会触发空指针的代码，请报告 BLOCK 级别问题。
```

分段使用 `# 标题` 格式，解析器提取各段内容。

### 加载顺序

1. 扫描内置 `ai_rules/` 目录，加载所有 `.md` 文件 → 解析为 `RuleDoc`
2. 扫描用户目录 `~/.code-review/rule-docs/`，加载所有 `.md` 文件 → 解析为 `RuleDoc`
3. 用户自定义规则与内置重名时，**用户定义覆盖内置**，方便用户定制

## Prompt 组装

### 拼接顺序

组装后的完整 prompt 结构：

```
--- System Prompt ---
你是一个专业的 Android 代码审查 AI。

# 输出格式要求
...（所有格式规则放在这里，固定不变）

--- Task Prompt ---
当前是 Diff 增量代码审查，请你重点关注本次变更的代码内容，
只分析改动部分，找出变更引入的潜在问题。

--- RuleDocs ---
以下是具体的审查规则，请你按照这些规则进行检查：

---
<RuleDoc 1 完整内容>
---
<RuleDoc 2 完整内容>
---
...（所有规则都在这里）

--- Code Input ---
以下是需要审查的代码：

${codeContent}
```

### 分隔符

使用 `---` 分隔不同层级，结构清晰，AI 容易识别边界。

## System Prompt / Task Prompt 文件位置

```
src/main/resources/ai_rules/
├── system-prompt.md      # System Prompt（固定）
├── task-diff.md          # Task Prompt - Diff 模式
└── task-global.md        # Task Prompt - Global 模式
```

内容拆分：
- 原有 `diff-review.md` → 格式部分提取到 `system-prompt.md`，任务说明到 `task-diff.md`
- 原有 `full-review.md` → 格式部分提取到 `system-prompt.md`，任务说明到 `task-global.md`

## 现有代码改造影响

| 模块 | 变化 |
|------|------|
| `AiFindingParser` | **完全不变**，输出协议保持原样 |
| `AiClient` 接口 | **完全不变**，只改变输入 prompt 生成方式 |
| `PromptLoader` | 保留但废弃，逐步迁移 |
| `MainScreen` | 修改调用方式：`PromptLoader` → `PromptAssembler` |
| GUI | **完全不变**，用户无感知 |
| 配置存储 | **完全不变** |

## 新增组件清单

| 新增组件 | 职责 |
|----------|------|
| `RuleDoc.kt` | 数据类 |
| `AiReviewContext.kt` | 数据类 |
| `RuleDocLoader.kt` | 加载解析 RuleDoc（内置 + 用户） |
| `PromptAssembler.kt` | 接口 + 默认实现 |
| `resources/ai_rules/` | 新增目录存放 RuleDoc |

## 迁移计划（Phase 1）

1. 创建新的数据结构 `RuleDoc`, `AiReviewContext`
2. 创建 `RuleDocLoader` 实现加载逻辑
3. 创建 `PromptAssembler` 接口和默认实现
4. 拆分原有提示词 → `system-prompt.md` + `task-diff.md` + `task-global.md`
5. 为 8 个内置本地规则各创建一个 RuleDoc 文件
6. 修改 `MainScreen` 调用新的组装接口
7. 测试验证功能正常

## 成功标准（Phase 1）

- [x] 程序正常启动，无编译错误
- [x] AI 审查功能正常工作
- [x] 输出结果格式正确，报告生成正常
- [x] 用户可在 `~/.code-review/rule-docs/` 添加自定义 RuleDoc
- [x] 所有现有功能保持不变
- [x] 架构分层清晰，为 Phase 2 标签检索预留接口

## 不包含在 Phase 1 中

- 标签检索（放到 Phase 2）
- embedding RAG（放到 Phase 3）
- 输出协议修改（保持不变）
- GUI 修改（用户无感知）
