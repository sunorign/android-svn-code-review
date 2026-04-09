# AI 审查 Prompt 架构升级设计文档
副标题：面向轻量 RAG 演进的分层改造方案

---

## 1. 文档目的

本文档用于指导 Code Review Kotlin 项目的 AI 审查模块，从当前“提示词加载驱动”升级为“Prompt 分层 + 规则知识注入 + 可演进 RAG 架构”。

目标是在不破坏现有报告结构和解析逻辑的前提下：

- 提升 AI 审查稳定性
- 避免未来提示词拼接导致的幻觉问题
- 建立可扩展的规则知识体系
- 为后续 RAG（检索增强）演进预留空间

---

## 2. 当前现状

当前系统具备：

- AI 审查能力（Claude / OpenRouter / Ollama）
- Diff / Global 两种提示词模板
- 支持加载外部提示词文件
- 使用 `<findings>` 结构解析输出
- HTML + Markdown 报告体系稳定

当前特点：

- 提示词是“按模式加载”，而不是拼接
- 外部文件已支持加载，但尚未分类（指令 vs 规则）

潜在风险（尚未发生，但未来会发生）：

1. 多提示词拼接导致上下文冲突
2. 指令 / 规则 / 输出格式混杂
3. 提示词体积膨胀
4. AI 输出不稳定（幻觉、泛化）

---

## 3. 改造目标

将 AI 审查从：

按模式加载 prompt

升级为：

固定 System Prompt
+ 固定 Task Prompt
+ RuleDoc（知识）
+ 可选检索
+ Code Input

---

## 4. 核心设计原则

1. Prompt 分层（职责隔离）
2. RuleDoc 替代提示词文件
3. 规则不直接拼接
4. 输出协议保持不变
5. 为 RAG 预留接口

---

## 5. 架构设计

### 5.1 新架构流程

代码输入
→ QueryAnalyzer
→ RuleRetriever（可选）
→ PromptAssembler
→ AI Provider
→ Parser
→ Report

---

## 6. Prompt 分层设计

### System Prompt（固定）
- 定义 AI 身份
- 限制行为（禁止猜测）

### Task Prompt（按模式）
- Diff：只关注改动
- Global：允许全局分析

### RuleDoc（知识）
- 审查规则
- 业务规则

### Code Input
- diff / file

---

## 7. RuleDoc 设计

RuleDoc ≠ Prompt

示例结构：

# 规则名
空指针风险

# 标签
null, java

# 场景
返回值未判空

# 风险
可能 NPE

---

## 8. 数据模型

```kotlin
data class RuleDoc(...)
data class RuleChunk(...)
data class RetrievalQuery(...)
data class AiReviewContext(...)
```

---

## 9. PromptAssembler

```kotlin
interface PromptAssembler {
    fun assemble(context: AiReviewContext): String
}
```

输出：

System
Task
Rules（可选）
Code

---

## 10. 输出协议

保持 `<findings>` 不变

扩展 metadata（不影响 HTML）：

```kotlin
data class FindingMetadata(...)
```

---

## 11. 实施计划

### Phase 1
- Prompt 分层
- RuleDoc 支持
- PromptAssembler

### Phase 2
- 标签检索
- metadata 输出

### Phase 3
- RAG（embedding）

---

## 12. 风险

- 不要修改 finding 协议
- 不要拼接全部规则
- 规则质量 > 算法

---

## 13. 成功标准

- Prompt 更短
- 幻觉下降
- 输出稳定
- 可解释性提升

---

## 14. 总结

从“提示词系统”升级为“审查引擎”



重点做这几块：

- PromptAssembler 设计（这是核心）
- RuleDoc / RuleChunk 数据结构
- QueryAnalyzer（标签提取）
- Phase1 最小可运行版本（不要一上来做 RAG）
