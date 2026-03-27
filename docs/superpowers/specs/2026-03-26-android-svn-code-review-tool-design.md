# Android SVN 代码审查工具设计

## 概述

这是一个面向 Android 开发团队的 SVN 提交前代码审查工具。使用 Python 开发，作为 SVN pre-commit 钩子运行，在提交代码前自动审查即将提交的改动，帮助团队在提交阶段发现常见问题和潜在 bug。

### 目标

- 在提交阶段拦截严重问题，减少后期代码评审成本
- 积累团队专属审查规则资产，逐步优化
- 结合本地静态规则检查和 AI 智能分析，兼顾速度和深度
- 适应 Java/Kotlin Android 原生开发场景

---

## 架构设计

```
android-code-review/
├── hooks/                    # SVN 钩子脚本
│   └── pre-commit            # pre-commit 钩子入口
├── src/
│   ├── main.py               # 主程序入口
│   ├── diff_parser.py        # SVN diff 解析器
│   ├── scanner.py            # 文件扫描器（处理过滤逻辑）
│   ├── local_rules/          # 本地静态规则模块
│   │   ├── __init__.py
│   │   ├── base_rule.py      # 规则基类（定义接口）
│   │   ├── java_rules/       # Java 规则集合
│   │   ├── android_rules/    # Android 特有规则
│   │   └── kotlin_rules/     # Kotlin 规则集合（预留）
│   ├── ai_reviewer/          # AI 审查模块
│   │   ├── __init__.py
│   │   ├── base_client.py    # API 客户端基类
│   │   ├── claude_client.py  # Claude API 客户端
│   │   ├── openrouter_client.py # OpenRouter 客户端
│   │   ├── local_ollama_client.py # 本地 Ollama 客户端（骨架预留）
│   │   └── prompt_templates/ # AI 提示词模板目录
│   │       ├── java-diff-review.md
│   │       ├── kotlin-diff-review.md
│   │       └── android-full-review.md
│   ├── reporter/             # 报告生成模块
│   │   ├── __init__.py
│   │   ├── text_reporter.py
│   │   ├── html_reporter.py
│   │   └── json_reporter.py
│   └── config.py             # 配置读取（环境变量）
├── docs/
│   ├── writing-local-rules.md      # 本地规则编写指南
│   └── writing-ai-prompts.md       # AI 提示词规范编写指南
└── output/                   # 审查输出目录（运行时创建）
```

**设计原则**：
- 规则模块化，易于扩展新增
- 提示词模板作为文本文件存储，方便团队积累优化
- 配置不进代码库，API 密钥从环境变量读取

---

## 审查流程设计

```
1. pre-commit 钩子被 SVN/TortoiseSVN 触发
   ↓
2. 调用 svn diff 获取本次提交的所有改动
   ↓
3. 按规则过滤文件：
      - 默认忽略 build/, app/build/, generated/ 等自动生成目录
      - 检查 libs/ 是否有变更 → 如果有，记录提醒，但不审查代码
   ↓
4. 对每个待审查文件的 diff 增量：
      a. 运行所有匹配的本地规则
      b. 收集问题，按 BLOCK/WARNING 分级
      c. 如果本地规则通过，且配置了 AI → 调用 AI 审查增量
   ↓
5. 如果存在 BLOCK 级问题：
      → TortoiseSVN 弹窗显示问题，阻止提交
      → 输出三份报告到 code-review-output/
      → 退出码非0，提交终止
   ↓
6. 如果 diff 审查通过：
      → 弹出对话框询问："Diff 审查通过，是否对修改文件做全文审查？"
      → 用户选"否" → 允许提交，输出报告，退出0
      → 用户选"是" → 继续全文审查，结果只给建议，不拦截，输出报告后允许提交
```

---

## 规则设计

### 规则分级

| 级别 | 说明 | 对提交影响 |
|------|------|------------|
| BLOCK | 阻断性问题（严重bug、安全漏洞） | 阻止提交 |
| WARNING | 警告（不规范但不一定错误） | 不阻止，仅记录 |

### 默认忽略目录

- `build/`
- `*/build/`
- `app/build/`
- `generated/`
- `*/generated/`

### 特殊处理：libs/ 目录

如果 `libs/` 目录下文件发生变更：
- **不做代码质量审查**
- 在报告中添加 **明确提醒**，要求提交者在提交日志中说明变更原因

### 初始内置规则

#### Java 规则
- [BLOCK] `System.out.println` / `Log.d` 调试日志残留
- [BLOCK] 硬编码的密码、密钥、API Key 等敏感信息
- [WARNING] 未关闭的 `Cursor`/`Stream`/`Connection`/`FileInputStream`
- [WARNING] 可能的 NPE 风险（未判空直接调用方法）
- [WARNING] 非静态内部类可能造成内存泄漏

#### Android 规则
- [WARNING] 硬编码的 IP/URL 地址（应该放在配置文件中）
- [WARNING] `ViewHolder` 模式使用不当
- [BLOCK] 二进制文件（`.apk`/`.dex`）不应该提交到代码库

---

## AI 审查模块设计

### 支持的 AI 服务

- **Anthropic Claude API** - 原生支持
- **OpenRouter** - 支持，可调用各种模型
- **Local Ollama** - 骨架预留，方便后续接入本地部署大模型

### 认证

API 密钥/地址从**环境变量读取**：
- `ANTHROPIC_API_KEY` - Claude API
- `OPENROUTER_API_KEY` - OpenRouter
- `OLLAMA_API_BASE` - Ollama 地址（默认 `http://localhost:11434`）

### 提示词模板管理

- 提示词模板以 `.md` 文件形式存放在 `ai_reviewer/prompt_templates/`
- 团队可以根据自身业务场景修改优化，积累成团队资产
- 内置初始模板：
  - `java-diff-review.md` - Java diff 增量审查
  - `kotlin-diff-review.md` - Kotlin diff 增量审查
  - `android-full-review.md` - Android 全文审查

### 审查策略

- **Diff 审查**：默认启用，只分析增量，token 消耗少
- **全文审查**：可选，diff 通过后由用户选择是否触发，更全面但消耗更多 token

---

## 输出报告设计

### 输出位置

项目根目录下的 `code-review-output/` 目录

### 输出文件

`review-result-YYYYMMDD-HHMMSS.[ext]`

| 格式 | 文件 | 说明 |
|------|------|------|
| 文本 | `.txt` | 纯文本摘要，终端可直接看 |
| HTML | `.html` | 格式化报告，带语法高亮，问题分组显示 |
| JSON | `.json` | 结构化数据，方便后续工具集成 |

### 报告内容

1. 审查基本信息：时间、模式、审查文件数量
2. BLOCK 级问题列表（带文件路径、行号、问题描述）
3. WARNING 级问题列表
4. AI 发现的问题列表
5. `libs/` 变更提醒（如果有）
6. 全文审查建议（如果执行了全文审查）

---

## 文档

必须包含两份文档供团队新人参考：

1. **`writing-local-rules.md`** - 本地静态规则编写指南
   - 规则接口说明
   - 如何新增规则步骤
   - 示例代码

2. **`writing-ai-prompts.md`** - AI 提示词编写规范
   - 如何写好提示词让 AI 输出结构化结果
   - 模板格式要求
   - 示例

---

## 成功标准

- [ ] SVN pre-commit 钩子能被 TortoiseSVN 正确触发
- [ ] 能正确解析 svn diff，过滤不需要审查的文件
- [ ] 本地规则能正确识别问题，BLOCK 问题阻止提交
- [ ] diff 通过后能弹出询问框让用户选择是否全文审查
- [ ] 同时支持 Claude API 和 OpenRouter
- [ ] Ollama 客户端骨架预留，接口对齐，方便后续实现
- [ ] 输出三种格式的报告到指定目录
- [ ] 两份编写指南文档完整清晰
