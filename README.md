# SuperPower Code Review - Android 客户端自动化代码审查工具

## 项目介绍

SuperPower Code Review 是一款专为 **Android 客户端开发人员** 设计的自动化代码审查工具，旨在帮助开发人员在提交代码前发现常见问题和潜在 bug，提高代码质量，减少后期代码评审成本。

这是一个客户端工具，支持**本地静态规则检查**和**AI 辅助审查**双重机制，提供用户友好的图形化界面，无需复杂配置，开箱即用。

团队维护多个 POS 项目（收单/收银台/MIS/MTMS），支持按项目加载规则，只检查你当前项目需要的规则。

## 核心特点

- **自动化审查流程**：支持 GUI 图形化操作，双击即可启动
- **项目级配置**：每个项目可以配置只加载需要的规则和 AI 提示词
- **双重审查机制**：结合本地静态规则检查和 AI 智能分析
- **智能过滤**：自动忽略 build/、generated/ 等自动生成目录
- **用户友好**：图形化界面选择项目目录，一键开始审查
- **统一表格格式报告**：支持文本、HTML 和 JSON 三种格式，均采用五列统一表格布局
- **易于扩展**：模块化架构，方便 Android 开发也能轻松新增规则

## 功能特性

### 本地静态规则检查

内置多种 Android 开发常用规则，按通用规则和项目规则分层管理：

#### 通用 Java 规则 (存放在 `src/local_rules/common_rules/`
- **[BLOCK] Java-DebugLogging**：检查 `System.out.println` 和 `Log.d` 等调试日志
- **[BLOCK] Java-HardcodedSecrets**：检测密码、密钥、API Key 等敏感信息
- **[WARNING] Java-UnclosedResources**：检查未关闭的 `Cursor`、`Stream`、`Connection`、`FileInputStream`
- **[WARNING] Java-NPERisk**：识别可能的空指针异常风险（未判空直接调用方法）
- **[WARNING] Java-MemoryLeak**：检测非静态内部类可能造成的内存泄漏

#### 通用 Android 规则
- **[WARNING] Android-HardcodedUrls**：检查硬编码的 IP 地址或 URL（应放在配置文件中）
- **[WARNING] Android-ViewHolderPattern**：检查 ViewHolder 模式的正确使用
- **[BLOCK] Android-BinaryFiles**：阻止提交 `.apk`、`.dex` 等二进制文件

#### Kotlin 规则
- 预留架构，支持扩展

#### POS 项目特有规则
每个项目放在 `src/local_rules/pos_project_rules/项目名称/`，你可以添加项目特有的业务规范规则。

### AI 辅助审查

支持多种 AI 服务提供商：

- **Anthropic Claude API**：原生支持
- **OpenRouter**：支持调用多种模型（预配置可用 API key，开箱即用
- **Local Ollama**：本地部署大模型（骨架预留）

AI 提示词也支持按项目配置，每个项目可以定义自己特有的审查要点。

## 目录结构说明

```
src/local_rules/                # 本地规则根目录
├── base_rule.py               # 所有规则的抽象基类（不用改）
├── common_rules/             # 通用规则池 - 所有项目共享
│   ├── java_rule_*.py        # Java 语言规则 → 文件名前缀 java_rule_ 一眼识别
│   ├── android_rule_*.py     # Android 框架规则 → 文件名前缀 android_rule_
│   └── kotlin_rule_*.py      # Kotlin 语言规则 → 文件名前缀 kotlin_rule_
└── pos_project_rules/         # POS 各项目特有规则 → 每个项目一个子目录
    ├── payment/              # 收单软件
    │   ├── __init__.py      # ← 这里配置 ENABLED_RULES 列出本项目启用哪些规则
    │   └── payment_*.py      # 收单项目特有规则
    ├── cashier/              # 收银台软件
    ├── mis/                 # MIS 通道软件
    └── mtms/                # MTMS 设备管理软件

src/ai_reviewer/
└── prompt_templates/        # AI 提示词 - 目录结构完全对齐 local_rules
    ├── common/              # 通用提示词
    │   ├── diff-review.md    # 默认增量审查提示词
    │   └── full-review.md  # 默认全量审查提示词
    └── pos_projects/        # 各项目提示词 - 目录名完全对应 local_rules
        ├── payment/
        │   ├── __init__.py  # ← ENABLED_PROMPTS 列出本项目启用哪些提示词
        │   └── *.md          # 每个提示词单独一个文件
        ├── cashier/
        ├── mis/
        └── mtms/
```

**文件名命名规范：**
| 类型 | 前缀 | 示例
|------|------|------
| Java 语言规则 | `java_rule_` | `java_rule_debug_logging.py`
| Android 框架规则 | `android_rule_` | `android_rule_hardcoded_urls.py`
| Kotlin 语言规则 | `kotlin_rule_` | `kotlin_rule_null_safety.py`
| 收单项目规则 | `payment_` | `payment_sensitive_keys.py`
| 收银台项目规则 | `cashier_` | `cashier_ui_standard.py`
| MIS 项目规则 | `mis_` | `mis_serial_port.py`
| MTMS 项目规则 | `mtms_` | `mtms_version_check.py`

## 环境要求

### 系统要求

- Windows 7 或更高版本（Windows 10/11 推荐）
- Python 3.8 或更高版本（需用户自行安装）

### 依赖库

```
requests>=2.28.0
```

### 可选依赖

如果使用 AI 审查功能，需要：
- 有效的 AI 服务 API 密钥（Claude 或 OpenRouter）
- 或本地 Ollama 服务（用于本地部署模型）

## 安装步骤

本工具为**客户端工具，开箱即用**，无需复杂安装：

### 第一步：克隆/下载项目到本地

将项目克隆或下载到您的本地计算机，例如 `D:/Documents/Projects/superpower-code-review/`。

### 第二步：检查配置文件

项目已预配置好 AI 客户端配置文件 `src/ai_reviewer/ai_client_config.json`，可直接使用。默认配置了 OpenRouter 提供商，API 密钥已预配置在文件中，如需切换 AI 模型，可直接编辑此文件。

### 第三步：启动工具

直接双击项目根目录下的 `start-gui.bat` 文件即可启动图形化界面。

## 客户端使用方法

### GUI 方式（推荐，简单易用）

1. **启动工具**：双击项目根目录下的 `start-gui.bat` 文件
2. **选择项目类型**：下拉框选择你的项目（默认选中收单软件
3. **选择项目目录**：在弹出的对话框中，选择您的 Android 项目根目录
4. **开始审查**：点击"开始代码审查"按钮
5. **查看报告**：等待审查完成，工具会自动在浏览器中打开 HTML 报告

### 命令行方式（高级用法，用于 SVN 钩子）

工具也支持通过命令行手动运行，支持 `--project` 参数指定项目：

```bash
cd D:/Documents/Projects/superpower-code-review
python src/main.py --project payment
```

#### 示例：手动测试审查功能

```bash
cd D:/AndroidProjects/PaymentApp
python D:/Documents/Projects/superpower-code-review/src/main.py --project payment
```

## 审查规则说明

### 规则分级

| 级别 | 说明 | 对提交影响 |
|------|------|------------|
| BLOCK | 严重问题（严重 bug、安全漏洞、内存泄露等） | 阻止提交，需立即修复 |
| WARNING | 一般问题（超时处理不足、代码不规范等） | 不阻止，但建议修复 |

### 默认忽略目录

工具默认忽略以下自动生成的目录：
- `build/` 及所有子目录下的 `build/`
- `app/build/`
- `generated/` 及所有子目录下的 `generated/`

### 特殊处理：libs/ 目录

如果 `libs/` 目录下的文件发生变更：
- 工具**不**对这些文件进行代码质量审查
- 但会在报告中添加明确的提醒，要求提交者在提交日志中说明变更原因

## 给 Android 开发扩展指南

### 如何新增一条本地规则

**你只需要会写一个 Python 文件，非常简单：**

#### 步骤 1：新建文件

- 如果是**通用规则** → 在 `src/local_rules/common_rules/` 按命名规范新建文件
- 如果是**项目特有规则** → 在 `src/local_rules/pos_project_rules/你的项目/` 新建文件

#### 步骤 2：复制模板写代码

复制现有规则文件，替换内容，只需要改：

```python
"""
一句话说明这个规则检查什么
"""
import re
from typing import List

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff

# 这里写你的匹配模式

class YourRuleName(BaseRule):

    @property
    def name(self) -> str:
        return "Java-YourRuleName"  # ← 报告中显示的规则名称

    @property
    def description(self) -> str:
        return "一句话说明这个规则检查什么"

    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        # 你的检查逻辑 → 对本次变更的每一行检查
        # 发现问题就 add RuleFinding
        return findings

    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        findings = []
        # 你的检查逻辑 → 对整个文件逐行检查
        # 发现问题就 add RuleFinding
        return findings
```

**RuleFinding 构造参数：**
```python
RuleFinding(
    file_path=file_diff.file_path,        # 文件路径
    line_number=change.line_number,       # 问题行号
    rule_name=self.name,                 # 规则名称
    message="问题描述说明",              # 问题描述
    severity="BLOCK",                  # BLOCK 或 WARNING
    code_snippet=content.strip()      # 问题代码片段（显示用）
)
```

**基类已经给你提供了帮助方法，直接用：

```python
# 判断这行是不是注释 → 返回 True/False
self._is_line_comment(content)

# 判断匹配到的内容是不是在字符串字面量里面 → 返回 True/False
self._is_pattern_in_string(line, match_start, match_end)

# 从内容中移除注释 → 返回移除注释后的内容
self._remove_comments(content)
```

#### 步骤 3：在项目配置中添加你的规则

打开 `src/local_rules/pos_project_rules/你的项目/__init__.py`，导入你的规则，加到 `ENABLED_RULES` 列表：

```python
# ... 其他导入 ...
from src.local_rules.pos_project_rules.your_project.your_rule_file import YourRuleClass

ENABLED_RULES = [
    # ... 其他规则 ...
    YourRuleClass(),  # ← 新增你的规则实例
]
```

搞定！下次启动工具就会加载你的规则了。

### 如何新增项目自定义 AI 提示词

1. 在 `src/ai_reviewer/prompt_templates/pos_projects/你的项目/` 新建 `.md` 文件
   - 文件名包含 `diff` → 自动识别为增量审查提示词
   - 文件名包含 `full` → 自动识别为全量审查提示词
   - 都不包含 → 默认按全量处理
2. 在同一个目录下的 `__init__.py` 把文件名加到 `ENABLED_PROMPTS` 列表：
   ```python
   ENABLED_PROMPTS = [
       "your-prompt-diff.md",
       "your-prompt-full.md",
   ]
   ```
3. 完成！工具会自动识别加载。

## 报告格式说明

所有报告格式均采用统一的五列表格结构，包含以下列：

| 列名 | 说明 |
|------|------|
| **优先级** | 问题严重程度：严重/一般/轻微 |
| **问题类型** | AI 分析的问题分类（如：内存泄露、超时处理不足、安全隐患等） |
| **位置** | 问题所在位置，格式为 `文件路径:行号` |
| **说明** | 问题的详细描述 |
| **修复建议** | AI 生成的具体修复建议 |

### 文本报告 (txt)

- Markdown 表格格式，适合在终端直接查看
- 使用标准 Markdown 语法，便于复制和分享

### HTML 报告 (html)

- 响应式 Bootstrap 表格样式
- 优先级使用不同颜色标识：严重红色，一般黄色，轻微蓝色
- 支持响应式布局，在不同设备上都有良好的显示效果
- 便于分享和查看

### JSON 报告 (json)

- 结构化的 JSON 格式，保持五列结构
- 包含所有审查信息的详细数据
- 适合与其他工具集成（如 CI/CD 系统）
- 便于自动化处理和分析

## 常见问题

### Q1: 工具无法连接到 SVN

**A**: 检查以下内容：

1. 确保 SVN 客户端已正确安装
2. 确保 SVN 命令在系统 PATH 中
3. 尝试在命令行中直接运行 `svn diff` 命令
4. 检查是否有网络连接问题

### Q2: AI 审查功能不工作

**A**: 检查以下内容：

1. 确保已配置正确的 API 密钥
2. 检查 API 密钥是否有效
3. 检查网络连接是否正常
4. 查看日志文件（`code_review_YYYYMMDD_HHMMSS.log`）获取详细错误信息

### Q3: 钩子脚本未被触发

**A**: 检查以下内容：

1. 确保钩子脚本已正确放置在 SVN 仓库的 `hooks` 目录下
2. 检查脚本是否具有执行权限
3. 尝试手动运行脚本进行测试
4. 检查 SVN 客户端的配置

### Q4: 如何暂时禁用代码审查

**A**: 您可以通过以下方法暂时禁用审查：

1. 重命名钩子脚本（例如，将 `pre-commit.bat` 改为 `pre-commit.disabled`）
2. 提交完成后再重新命名回来
3. **注意**：这样做会完全禁用审查，不建议频繁使用

### Q5: 工具运行缓慢

**A**: 如果工具运行缓慢，可能是以下原因：

1. **AI 审查**：如果配置了 AI 审查，API 响应时间可能会影响速度
2. **大文件**：如果提交包含非常大的文件，处理时间会增加
3. **规则数量**：过多的自定义规则会增加处理时间
4. **网络问题**：如果使用远程 AI 服务，网络延迟会影响速度

**优化建议**：

1. 考虑禁用不需要的规则
2. 优化自定义规则的实现
3. 对于非常大的文件，考虑临时忽略
4. 考虑使用本地部署的 Ollama 服务

### Q6: 如何忽略特定文件或目录

**A**: 目前工具通过硬编码的方式忽略自动生成目录。如果需要添加更多忽略规则，可以修改 `src/scanner.py` 文件中的 `DEFAULT_IGNORE_PATTERNS` 列表（使用 glob 风格模式）：

```python
# src/scanner.py
DEFAULT_IGNORE_PATTERNS = [
    'build/',
    '*/build/',
    'app/build/',
    'generated/',
    '*/generated/',
    '.git/',
    '.svn/',
    'my_custom_directory/',  # ← 新增忽略规则
    '*/my_custom_directory/',
]
```

## 附录：SVN pre-commit 服务端钩子配置

### 配置 SVN 钩子

#### 方法一：直接使用项目提供的钩子（推荐）

1. 找到您的 SVN 仓库的 `hooks` 目录
2. 将项目中 `hooks/pre-commit` 钩子脚本复制到仓库的 `hooks` 目录中
3. 确保脚本具有执行权限（Windows 系统通常不需要额外配置）

#### 方法二：手动创建钩子脚本

在 SVN 仓库的 `hooks` 目录下创建 `pre-commit.bat`（Windows 系统）文件：

```batch
@echo off
D:/Python39/python.exe D:/Documents/Projects/superpower-code-review/src/main.py --project payment
if %errorlevel% neq 0 (
    echo.
    echo 代码审查失败，请查看审查报告
    exit /b 1
)
exit /b 0
```

**注意**：请根据您的实际 Python 安装路径和项目路径进行修改，`--project` 参数指定你的项目。

### 验证安装

在 SVN 仓库中进行一次提交测试，钩子应该会自动触发。如果钩子未触发，请检查以下内容：
- 钩子脚本是否正确放置在 `hooks` 目录中
- 脚本是否具有执行权限
- Python 路径是否正确
- 项目路径是否正确

### 配置说明

所有配置都通过环境变量进行管理，无需修改代码。

#### 通用配置
```
API_TIMEOUT=60                  # API 超时时间（秒）
AI_REVIEW_PROVIDER=claude       # 可选：claude/openrouter/ollama
```

#### Claude API 配置
```
ANTHROPIC_API_KEY=your_api_key   # 您的 Claude API 密钥
ANTHROPIC_API_URL=https://api.anthropic.com/v1  # API 地址
ANTHROPIC_MODEL=claude-3-opus-20240229  # 模型名称
ANTHROPIC_MAX_TOKENS=4096       # 最大 token 数
```

#### OpenRouter 配置
```
OPENROUTER_API_KEY=your_api_key  # 您的 OpenRouter API 密钥
OPENROUTER_API_URL=https://openrouter.ai/api/v1  # API 地址
OPENROUTER_MODEL=gpt-4-turbo-preview  # 模型名称
OPENROUTER_MAX_TOKENS=4096      # 最大 token 数
```

#### Local Ollama 配置
```
OLLAMA_API_BASE=http://localhost:11434  # Ollama 服务地址
OLLAMA_MODEL=llama2                # 模型名称
OLLAMA_MAX_TOKENS=4096            # 最大 token 数
```

### 配置方法（Windows）

1. 右键点击"此电脑" -> 属性 -> 高级系统设置 -> 环境变量
2. 在系统变量中添加或修改上述环境变量
3. 重新启动 SVN 客户端或命令行窗口使配置生效
