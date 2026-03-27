# SuperPower Code Review - Android SVN 自动化代码审查工具

## 项目介绍

SuperPower Code Review 是一款专为 Android 开发团队设计的 SVN 提交前自动化代码审查工具。它结合了静态代码分析和 AI 辅助审查功能，帮助开发团队在代码提交阶段发现常见问题和潜在 bug，提高代码质量，减少后期代码评审成本。

### 核心特点

- **自动化审查流程**：作为 SVN pre-commit 钩子运行，无需人工干预
- **双重审查机制**：结合本地静态规则检查和 AI 智能分析
- **智能过滤**：自动忽略 build/、generated/ 等自动生成目录
- **用户友好**：图形化界面询问是否需要全文 AI 审查
- **统一表格格式报告**：支持文本、HTML 和 JSON 三种格式，均采用五列统一表格布局
- **易于扩展**：模块化架构，支持新增本地规则和 AI 提供商

## 功能特性

### 本地静态规则检查

内置多种 Android 开发常用规则：

#### Java 规则
- **[BLOCK] Java-DebugLogging**：检查 `System.out.println` 和 `Log.d` 等调试日志
- **[BLOCK] Java-HardcodedSecrets**：检测密码、密钥、API Key 等敏感信息
- **[WARNING] Java-UnclosedResources**：检查未关闭的 `Cursor`、`Stream`、`Connection`、`FileInputStream`
- **[WARNING] Java-NPERisk**：识别可能的空指针异常风险（未判空直接调用方法）
- **[WARNING] Java-MemoryLeak**：检测非静态内部类可能造成的内存泄漏

#### Android 规则
- **[WARNING] Android-HardcodedUrls**：检查硬编码的 IP 地址或 URL（应放在配置文件中）
- **[WARNING] Android-ViewHolderPattern**：检查 ViewHolder 模式的正确使用
- **[BLOCK] Android-BinaryFiles**：阻止提交 `.apk`、`.dex` 等二进制文件

#### Kotlin 规则
- 预留架构，支持扩展

### AI 辅助审查

支持多种 AI 服务提供商：

- **Anthropic Claude API**：原生支持
- **OpenRouter**：支持调用多种模型
- **Local Ollama**：本地部署大模型（骨架预留）

### 审查流程

1. SVN pre-commit 钩子被触发
2. 获取本次提交的 diff 内容
3. 解析 diff 并扫描文件（过滤自动生成目录）
4. 运行本地静态规则检查
5. 如果发现 BLOCK 级问题，阻止提交并生成报告
6. 如果通过，弹出对话框询问是否进行全文 AI 审查
7. 可选：运行 AI 审查
8. 生成三种格式的审查报告

## 环境要求

### 系统要求

- Windows 7 或更高版本（Windows 10/11 推荐）
- SVN 客户端（TortoiseSVN 或命令行客户端）
- Python 3.8 或更高版本

### 依赖库

```
requests>=2.28.0
```

### 可选依赖

如果使用 AI 审查功能，需要：

- 有效的 AI 服务 API 密钥（Claude 或 OpenRouter）
- 或本地 Ollama 服务（用于本地部署模型）

## 安装步骤

### 1. 安装 Python 依赖

```bash
cd D:/Documents/Projects/projects_pycharm/superpowertest
pip install -r requirements.txt
```

### 2. 配置 SVN 钩子

#### 方法一：直接使用项目提供的钩子（推荐）

1. 找到您的 SVN 仓库的 `hooks` 目录
2. 将项目中 `hooks/pre-commit` 钩子脚本复制到仓库的 `hooks` 目录中
3. 确保脚本具有执行权限（Windows 系统通常不需要额外配置）

#### 方法二：手动创建钩子脚本

在 SVN 仓库的 `hooks` 目录下创建 `pre-commit.bat`（Windows 系统）文件：

```batch
@echo off
D:/Python39/python.exe D:/Documents/Projects/projects_pycharm/superpowertest/src/main.py
if %errorlevel% neq 0 (
    echo.
    echo 代码审查失败，请查看审查报告
    exit /b 1
)
exit /b 0
```

**注意**：请根据您的实际 Python 安装路径和项目路径进行修改。

### 3. 验证安装

在 SVN 仓库中进行一次提交测试，钩子应该会自动触发。如果钩子未触发，请检查以下内容：

- 钩子脚本是否正确放置在 `hooks` 目录中
- 脚本是否具有执行权限
- Python 路径是否正确
- 项目路径是否正确

## 配置说明

### 环境变量配置

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

## 使用方法

### 命令行参数

工具主要通过 SVN 钩子自动触发，但也可以手动运行进行测试。

```bash
cd D:/Documents/Projects/projects_pycharm/superpowertest
python src/main.py
```

### 使用示例

#### 示例 1：正常使用（作为 SVN 钩子）

1. 在 Android 项目中修改代码
2. 右键点击项目 -> TortoiseSVN -> 提交
3. 工具自动运行，显示审查进度
4. 如果有问题，会显示阻止提交的信息
5. 查看 `code-review-output` 目录下的审查报告

#### 示例 2：手动测试审查功能

```bash
cd D:/AndroidProjects/MyApp
python D:/Documents/Projects/projects_pycharm/superpowertest/src/main.py
```

#### 示例 3：查看审查报告

审查报告生成在项目根目录的 `code-review-output/` 目录下，包含以下文件：

- `review-result-YYYYMMDD-HHMMSS.txt` - 纯文本报告（适合终端查看）
- `review-result-YYYYMMDD-HHMMSS.html` - 格式化 HTML 报告（带语法高亮）
- `review-result-YYYYMMDD-HHMMSS.json` - 结构化 JSON 报告（适合工具集成）

### 报告示例

**文本报告示例（Markdown 表格格式）：**

```
代码审查报告
=============

| 优先级 | 问题类型       | 位置                  | 说明                     | 修复建议                     |
|--------|---------------|-----------------------|--------------------------|------------------------------|
| 严重   | 内存泄露       | MainActivity.java:120 | Handler 持有外部类引用   | 使用静态内部类 + WeakReference |
| 一般   | 超时处理不足   | ApiClient.java:85     | 网络请求超时设置过短     | 增加超时时间到 30 秒         |
| 轻微   | 代码风格       | Utils.java:42         | 未使用 try-with-resources| 改用 try-with-resources 语法 |
```

**HTML 报告示例（Bootstrap 样式）：**

```html
<table class="table table-bordered table-hover">
  <thead class="thead-light">
    <tr>
      <th>优先级</th>
      <th>问题类型</th>
      <th>位置</th>
      <th>说明</th>
      <th>修复建议</th>
    </tr>
  </thead>
  <tbody>
    <tr class="danger">
      <td><span class="badge badge-danger">严重</span></td>
      <td>内存泄露</td>
      <td>MainActivity.java:120</td>
      <td>Handler 持有外部类引用</td>
      <td>使用静态内部类 + WeakReference</td>
    </tr>
    <tr class="warning">
      <td><span class="badge badge-warning">一般</span></td>
      <td>超时处理不足</td>
      <td>ApiClient.java:85</td>
      <td>网络请求超时设置过短</td>
      <td>增加超时时间到 30 秒</td>
    </tr>
    <tr class="info">
      <td><span class="badge badge-info">轻微</span></td>
      <td>代码风格</td>
      <td>Utils.java:42</td>
      <td>未使用 try-with-resources</td>
      <td>改用 try-with-resources 语法</td>
    </tr>
  </tbody>
</table>
```

## 审查规则说明

### 规则分级

| 级别 | 说明 | 对提交影响 |
|------|------|------------|
| 严重 | 严重问题（严重 bug、安全漏洞、内存泄露等） | 阻止提交，需立即修复 |
| 一般 | 一般问题（超时处理不足、代码不规范等） | 不阻止，但建议修复 |
| 轻微 | 轻微问题（代码风格、优化建议等） | 不阻止，可以后续修复 |

### 默认忽略目录

工具默认忽略以下自动生成的目录：

- `build/` 及所有子目录下的 `build/`
- `app/build/`
- `generated/` 及所有子目录下的 `generated/`

### 特殊处理：libs/ 目录

如果 `libs/` 目录下的文件发生变更：

- 工具**不**对这些文件进行代码质量审查
- 但会在报告中添加明确的提醒，要求提交者在提交日志中说明变更原因

### 规则扩展

如果需要添加自定义规则，请参考 [扩展开发指南](#扩展开发指南) 章节。

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
- 可在支持 Markdown 的编辑器中渲染为表格
- 格式简洁，信息密度高

### HTML 报告 (html)

- 响应式 Bootstrap 表格样式
- 优先级使用不同颜色标识：
  - 严重：红色背景
  - 一般：黄色背景
  - 轻微：蓝色背景
- 支持响应式布局，在不同设备上都有良好的显示效果
- 便于分享和查看

### JSON 报告 (json)

- 结构化的 JSON 格式，保持五列结构
- 包含所有审查信息的详细数据
- 适合与其他工具集成（如 CI/CD 系统）
- 便于自动化处理和分析
- JSON 结构示例：
  ```json
  {
    "generated": "2026-03-27T14:27:15Z",
    "mode": "full-review",
    "file_count": 15,
    "findings": [
      {
        "优先级": "严重",
        "问题类型": "内存泄露",
        "位置": "MainActivity.java:120",
        "说明": "Handler 持有外部类引用",
        "修复建议": "使用静态内部类 + WeakReference"
      }
    ]
  }
  ```

## 扩展开发指南

### 新增本地静态规则

1. 在 `src/local_rules/` 目录下选择或创建合适的子目录（如 `java_rules/` 或 `android_rules/`）
2. 创建新的规则类，继承自 `BaseRule` 基类
3. 实现 `check_diff` 和 `check_full_file` 方法
4. 在该目录的 `__init__.py` 文件中导出新规则

#### 示例：新增 Java 规则

```python
# src/local_rules/java_rules/custom_rule.py
from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff

class CustomRule(BaseRule):
    name = "CustomRule"
    description = "自定义规则示例"

    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> list[RuleFinding]:
        findings = []
        # 实现增量检查逻辑
        # 示例：检查是否包含特定字符串
        if "TODO: 待完成" in change.content:
            findings.append(RuleFinding(
                file_path=file_diff.file_path,
                line_number=change.line_number,
                rule_name=self.name,
                message="发现未完成的 TODO 标记",
                severity="WARNING",
                code_snippet=change.content
            ))
        return findings

    def check_full_file(self, file_path: str, content: str) -> list[RuleFinding]:
        findings = []
        # 实现全文检查逻辑
        return findings
```

然后在 `src/local_rules/java_rules/__init__.py` 中导出：

```python
from .debug_logging import DebugLoggingRule
from .hardcoded_secrets import HardcodedSecretsRule
from .unclosed_resources import UnclosedResourcesRule
from .npe_risk import NPERiskRule
from .memory_leak import MemoryLeakRule
from .custom_rule import CustomRule  # 新增

JAVARULES = [
    DebugLoggingRule(),
    HardcodedSecretsRule(),
    UnclosedResourcesRule(),
    NPERiskRule(),
    MemoryLeakRule(),
    CustomRule(),  # 新增
]
```

### 新增 AI 提供商支持

1. 在 `src/ai_reviewer/` 目录下创建新的客户端类
2. 继承自 `BaseClient` 基类
3. 实现 `review_code` 方法
4. 在 `src/ai_reviewer/__init__.py` 中更新工厂函数

#### 示例：新增自定义 AI 客户端

```python
# src/ai_reviewer/custom_ai_client.py
from src.ai_reviewer.base_client import BaseAIClient
from src.ai_reviewer.prompt_templates import load_prompt_template

class CustomAIClient(BaseAIClient):
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.custom_api_key

    def review_diff(self, file_path: str, diff_content: str, prompt_template: str) -> AIReviewResult:
        # 实现增量审查逻辑
        prompt = load_prompt_template(prompt_template).format(
            file_path=file_path,
            file_content=diff_content
        )

        # 调用自定义 AI API
        response = self._call_api(prompt)

        # 解析 AI 响应并返回 findings
        return self._parse_response(response)

    def review_full_file(self, file_path: str, content: str, prompt_template: str) -> AIReviewResult:
        # 实现全文审查逻辑
        prompt = load_prompt_template(prompt_template).format(
            file_path=file_path,
            file_content=content
        )

        # 调用自定义 AI API
        response = self._call_api(prompt)

        # 解析 AI 响应并返回 findings
        return self._parse_response(response)
```

然后在 `src/ai_reviewer/__init__.py` 中更新：

```python
from src.ai_reviewer.claude_client import ClaudeClient
from src.ai_reviewer.openrouter_client import OpenRouterClient
from src.ai_reviewer.local_ollama_client import LocalOllamaClient
from src.ai_reviewer.custom_ai_client import CustomAIClient  # 新增

def get_ai_client(config: Config) -> Optional[BaseAIClient]:
    """Factory method to get the configured AI client."""
    provider = config.get_active_provider()
    if not provider:
        return None

    match provider:
        case 'claude':
            return ClaudeClient(config)
        case 'openrouter':
            return OpenRouterClient(config)
        case 'ollama':
            return LocalOllamaClient(config)
        case 'custom':
            return CustomAIClient(config)
        case _:
            logger.warning(f"Unknown AI provider: {provider}")
            return None
```

### 修改 AI 提示词模板

提示词模板位于 `src/ai_reviewer/prompt_templates/` 目录下，以 Markdown 格式存储。您可以根据需要修改这些模板。

#### 提示词模板示例

```markdown
# Java 代码审查

请帮我审查以下 Java 代码：

## 文件信息
- 文件路径：{file_path}

## 代码内容
```java
{file_content}
```

## 审查要求

1. 检查代码中的语法错误
2. 检查潜在的运行时错误（如空指针异常）
3. 检查代码的安全性问题
4. 检查代码的性能问题
5. 检查代码的可维护性
6. 提供优化建议

## 输出格式

请以 JSON 格式返回审查结果，结构如下：

```json
[
    {
        "file_path": "{file_path}",
        "line_number": 10,
        "rule_name": "语法错误",
        "description": "缺少分号",
        "severity": "BLOCK"
    }
]
```

## 常见问题

### Q1: 工具无法连接到 SVN

**A**: 检查以下内容：

1. 确保 SVN 客户端已正确安装
2. 确保 SVN 命令在系统 PATH 中
3. 尝试在命令行中直接运行 `svn diff` 命令
4. 检查是否有网络连接问题

### Q2: AI 审查功能不工作

**A**: 检查以下内容：

1. 确保已配置正确的环境变量
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
    'my_custom_directory/',  # 新增忽略规则
    '*/my_custom_directory/',
]
```
