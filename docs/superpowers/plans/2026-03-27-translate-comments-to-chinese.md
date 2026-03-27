# 注释中文化与使用手册编写 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将项目所有 Python 源代码中的英文注释翻译为中文，并在项目根目录生成一份完整的中文使用手册。

**Architecture:** 采用逐文件处理策略，逐个读取源码文件，翻译注释后写回。只修改注释内容，保持代码逻辑、变量命名、格式完全不变。最后生成根目录 `README.md` 使用手册。

**Tech Stack:** Python 代码库，只需要文本编辑，无需引入新依赖。

---

## 文件修改概览

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `src/main.py` | 修改 | 翻译主入口文件注释 |
| `src/config.py` | 修改 | 翻译配置模块注释 |
| `src/diff_parser.py` | 修改 | 翻译差异解析器注释 |
| `src/scanner.py` | 修改 | 翻译扫描器注释 |
| `src/ai_reviewer/base_client.py` | 修改 | 翻译 AI 客户端基类注释 |
| `src/ai_reviewer/claude_client.py` | 修改 | 翻译 Claude 客户端注释 |
| `src/ai_reviewer/openrouter_client.py` | 修改 | 翻译 OpenRouter 客户端注释 |
| `src/ai_reviewer/local_ollama_client.py` | 修改 | 翻译 Ollama 客户端注释 |
| `src/reporter/base_reporter.py` | 修改 | 翻译报告基类注释 |
| `src/reporter/text_reporter.py` | 修改 | 翻译文本报告注释 |
| `src/reporter/html_reporter.py` | 修改 | 翻译 HTML 报告注释 |
| `src/reporter/json_reporter.py` | 修改 | 翻译 JSON 报告注释 |
| `src/local_rules/base_rule.py` | 修改 | 翻译规则基类注释 |
| `src/local_rules/java_rules/debug_logging.py` | 修改 | 翻译调试日志规则注释 |
| `src/local_rules/java_rules/hardcoded_secrets.py` | 修改 | 翻译硬编码密钥规则注释 |
| `src/local_rules/java_rules/npe_risk.py` | 修改 | 翻译空指针风险规则注释 |
| `src/local_rules/java_rules/memory_leak.py` | 修改 | 翻译内存泄漏规则注释 |
| `src/local_rules/java_rules/unclosed_resources.py` | 修改 | 翻译未关闭资源规则注释 |
| `src/local_rules/android_rules/hardcoded_urls.py` | 修改 | 翻译硬编码 URL 规则注释 |
| `src/local_rules/android_rules/binary_files.py` | 修改 | 翻译二进制文件规则注释 |
| `src/local_rules/android_rules/viewholder_pattern.py` | 修改 | 翻译 ViewHolder 规则注释 |
| `README.md` | 新建 | 生成中文使用手册 |

---

### 任务组一：主模块文件注释翻译

### 任务 1：翻译 src/main.py 注释

**文件：**
- 修改: `src/main.py`

- [ ] **Step 1: 读取文件内容**

  使用 Read 工具读取完整文件。

- [ ] **Step 2: 将所有英文注释翻译为中文**

  逐行翻译注释，保持代码逻辑缩进不变。

- [ ] **Step 3: 写回文件并验证 Python 语法正确**

  使用 Write 工具写回，运行 `python -m py_compile src/main.py` 验证语法。

- [ ] **Step 4: 提交更改**

  ```bash
  git add src/main.py
  git commit -m "chore: translate comments in main.py to Chinese"
  ```

### 任务 2：翻译 src/config.py 注释

**文件：**
- 修改: `src/config.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/config.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/config.py
  git commit -m "chore: translate comments in config.py to Chinese"
  ```

### 任务 3：翻译 src/diff_parser.py 注释

**文件：**
- 修改: `src/diff_parser.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/diff_parser.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/diff_parser.py
  git commit -m "chore: translate comments in diff_parser.py to Chinese"
  ```

### 任务 4：翻译 src/scanner.py 注释

**文件：**
- 修改: `src/scanner.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/scanner.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/scanner.py
  git commit -m "chore: translate comments in scanner.py to Chinese"
  ```

---

### 任务组二：AI 审查模块注释翻译

### 任务 5：翻译 src/ai_reviewer/base_client.py 注释

**文件：**
- 修改: `src/ai_reviewer/base_client.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/ai_reviewer/base_client.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/ai_reviewer/base_client.py
  git commit -m "chore: translate comments in base_client.py to Chinese"
  ```

### 任务 6：翻译 src/ai_reviewer/claude_client.py 注释

**文件：**
- 修改: `src/ai_reviewer/claude_client.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/ai_reviewer/claude_client.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/ai_reviewer/claude_client.py
  git commit -m "chore: translate comments in claude_client.py to Chinese"
  ```

### 任务 7：翻译 src/ai_reviewer/openrouter_client.py 注释

**文件：**
- 修改: `src/ai_reviewer/openrouter_client.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/ai_reviewer/openrouter_client.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/ai_reviewer/openrouter_client.py
  git commit -m "chore: translate comments in openrouter_client.py to Chinese"
  ```

### 任务 8：翻译 src/ai_reviewer/local_ollama_client.py 注释

**文件：**
- 修改: `src/ai_reviewer/local_ollama_client.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/ai_reviewer/local_ollama_client.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/ai_reviewer/local_ollama_client.py
  git commit -m "chore: translate comments in local_ollama_client.py to Chinese"
  ```

---

### 任务组三：报告生成模块注释翻译

### 任务 9：翻译 src/reporter/base_reporter.py 注释

**文件：**
- 修改: `src/reporter/base_reporter.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/reporter/base_reporter.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/reporter/base_reporter.py
  git commit -m "chore: translate comments in base_reporter.py to Chinese"
  ```

### 任务 10：翻译 src/reporter/text_reporter.py 注释

**文件：**
- 修改: `src/reporter/text_reporter.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/reporter/text_reporter.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/reporter/text_reporter.py
  git commit -m "chore: translate comments in text_reporter.py to Chinese"
  ```

### 任务 11：翻译 src/reporter/html_reporter.py 注释

**文件：**
- 修改: `src/reporter/html_reporter.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/reporter/html_reporter.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/reporter/html_reporter.py
  git commit -m "chore: translate comments in html_reporter.py to Chinese"
  ```

### 任务 12：翻译 src/reporter/json_reporter.py 注释

**文件：**
- 修改: `src/reporter/json_reporter.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/reporter/json_reporter.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/reporter/json_reporter.py
  git commit -m "chore: translate comments in json_reporter.py to Chinese"
  ```

---

### 任务组四：本地规则模块注释翻译

### 任务 13：翻译 src/local_rules/base_rule.py 注释

**文件：**
- 修改: `src/local_rules/base_rule.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/local_rules/base_rule.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/local_rules/base_rule.py
  git commit -m "chore: translate comments in base_rule.py to Chinese"
  ```

### 任务 14：翻译 Java 规则 - debug_logging.py

**文件：**
- 修改: `src/local_rules/java_rules/debug_logging.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/local_rules/java_rules/debug_logging.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/local_rules/java_rules/debug_logging.py
  git commit -m "chore: translate comments in debug_logging.py to Chinese"
  ```

### 任务 15：翻译 Java 规则 - hardcoded_secrets.py

**文件：**
- 修改: `src/local_rules/java_rules/hardcoded_secrets.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/local_rules/java_rules/hardcoded_secrets.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/local_rules/java_rules/hardcoded_secrets.py
  git commit -m "chore: translate comments in hardcoded_secrets.py to Chinese"
  ```

### 任务 16：翻译 Java 规则 - npe_risk.py

**文件：**
- 修改: `src/local_rules/java_rules/npe_risk.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/local_rules/java_rules/npe_risk.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/local_rules/java_rules/npe_risk.py
  git commit -m "chore: translate comments in npe_risk.py to Chinese"
  ```

### 任务 17：翻译 Java 规则 - memory_leak.py

**文件：**
- 修改: `src/local_rules/java_rules/memory_leak.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/local_rules/java_rules/memory_leak.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/local_rules/java_rules/memory_leak.py
  git commit -m "chore: translate comments in memory_leak.py to Chinese"
  ```

### 任务 18：翻译 Java 规则 - unclosed_resources.py

**文件：**
- 修改: `src/local_rules/java_rules/unclosed_resources.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/local_rules/java_rules/unclosed_resources.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/local_rules/java_rules/unclosed_resources.py
  git commit -m "chore: translate comments in unclosed_resources.py to Chinese"
  ```

### 任务 19：翻译 Android 规则 - hardcoded_urls.py

**文件：**
- 修改: `src/local_rules/android_rules/hardcoded_urls.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/local_rules/android_rules/hardcoded_urls.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/local_rules/android_rules/hardcoded_urls.py
  git commit -m "chore: translate comments in hardcoded_urls.py to Chinese"
  ```

### 任务 20：翻译 Android 规则 - binary_files.py

**文件：**
- 修改: `src/local_rules/android_rules/binary_files.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/local_rules/android_rules/binary_files.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/local_rules/android_rules/binary_files.py
  git commit -m "chore: translate comments in binary_files.py to Chinese"
  ```

### 任务 21：翻译 Android 规则 - viewholder_pattern.py

**文件：**
- 修改: `src/local_rules/android_rules/viewholder_pattern.py`

- [ ] **Step 1: 读取文件内容**
- [ ] **Step 2: 将所有英文注释翻译为中文**
- [ ] **Step 3: 写回文件并验证 Python 语法正确**
  ```bash
  python -m py_compile src/local_rules/android_rules/viewholder_pattern.py
  ```
- [ ] **Step 4: 提交更改**
  ```bash
  git add src/local_rules/android_rules/viewholder_pattern.py
  git commit -m "chore: translate comments in viewholder_pattern.py to Chinese"
  ```

---

### 任务组五：生成中文使用手册

### 任务 22：生成根目录 README.md 中文使用手册

**文件：**
- 创建: `README.md`

- [ ] **Step 1: 编写完整中文使用手册**

  包含以下章节：
  - 项目介绍
  - 功能特性
  - 环境要求
  - 安装步骤
  - 配置说明（环境变量、AI 配置）
  - 使用方法（命令行参数、示例）
  - 审查规则说明
  - 报告格式说明
  - 扩展开发指南
  - 常见问题

- [ ] **Step 2: 验证文件格式正确**

- [ ] **Step 3: 提交更改**
  ```bash
  git add README.md
  git commit -m "docs: add Chinese user manual"
  ```

### 任务 23：最终验证 - 运行所有测试确保功能正常

**文件：**
- 所有已修改文件

- [ ] **Step 1: 运行所有现有测试**
  ```bash
  python -m pytest *.py -v
  ```
  预期：所有测试通过

- [ ] **Step 2: 验证主程序可以正常启动**
  ```bash
  python src/main.py --help
  ```
  预期：显示帮助信息，无语法错误

---

## 自审检查

- ✅ 规范覆盖率：所有注释翻译任务已覆盖源码文件，包含使用手册生成任务
- ✅ 无占位符：所有步骤都有明确指令和命令
- ✅ 一致性：文件路径正确，任务顺序合理
- ✅ 颗粒度：每个任务都是独立可执行的，步骤清晰

