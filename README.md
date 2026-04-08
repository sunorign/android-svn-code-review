# Code Review - Kotlin 版本

> Android 客户端自动化代码审查工具 - Kotlin + Compose Multiplatform 版本

## 项目介绍

Code Review 是一款专为 **Android 客户端开发人员** 设计的自动化代码审查工具，旨在帮助开发人员在提交代码前发现常见问题和潜在 bug，提高代码质量，减少后期代码评审成本。

这是 Kotlin 版本，使用 Gradle 构建，可以直接打包成 Windows `.exe` 可执行文件，开箱即用。

- 支持**本地静态规则检查**和 **AI 辅助审查** 双重机制，可灵活切换是否启用 AI
- 提供用户友好的**图形化界面**，无需复杂配置
- **按项目分类管理**规则和 AI 提示词，只检查当前项目需要的规则
- 支持三种扫描模式：全局扫描全量代码、SVN Diff 扫描变更文件、Git Diff 扫描变更文件
- Diff 模式仅扫描修改过的文件，扫描速度更快
- 支持 GUI 双击启动，也支持 **CLI 命令行** 集成到 SVN/Git 钩子
- 生成**HTML 简洁报告**（用于快速查看）和 **纯文本完整日志**（用于存档分享）
- 不再生成 TXT 和 JSON 格式的报告
- 改进的 AI 解析算法，使用标签包裹格式，大幅提高解析成功率
- 支持 `alwaysDisplay` 固定显示规则，即使未发现问题也会在报告中展示为绿色 PASS
- 修复提示词覆盖问题，AI 更容易记住输出格式要求
- 在日志中记录分析文件列表，方便追踪调试

## 功能特性

### 扫描模式

Code Review 提供三种扫描模式，以满足不同场景的需求：

#### 全局扫描
- 扫描项目中的所有源文件
- 适合初次使用或重大重构后的全面代码审查
- 检查范围最全面，但扫描时间较长

#### SVN Diff 模式
- 仅扫描 SVN 版本控制中**修改过的文件**
- 需要配置 SVN 环境
- 扫描速度快，适合日常开发中的增量代码审查

#### Git Diff 模式
- 仅扫描 Git 版本控制中**修改过的文件**
- 需要配置 Git 环境
- 扫描速度快，适合日常开发中的增量代码审查

> **提示**：Diff 模式（SVN 或 Git）只检查变更文件，相比全局扫描速度显著提升，是日常开发的推荐使用方式。

### 本地静态规则检查

#### 严重级别说明

| 级别 | 颜色 | 说明 |
|------|------|------|
| BLOCK | 红色 | 必须修复的问题 |
| WARNING | 黄色 | 需要关注的问题 |

#### 固定显示规则

对于重要的规则，可以设置 `alwaysDisplay = true`，这样即使本次扫描**未发现问题**，也会在 HTML 报告中额外添加一行绿色 PASS：

| 优先级 | 规则名称 | 位置 | 问题描述 | 代码片段 |
|--------|----------|------|----------|----------|
| PASS | Java-DebugLogging | - | 未发现问题 ✓ | - |

#### 通用 Java 规则
- **[BLOCK] Java-DebugLogging**：检查 `System.out.println` 和 `Log.d`/`Log.v` 调试日志
- **[BLOCK] Java-HardcodedSecrets**：检测密码、密钥、API Key 等硬编码敏感信息
- **[WARNING] Java-UnclosedResources**：检查未关闭的 Cursor/Stream/Connection 资源
- **[WARNING] Java-NPERisk**：识别多级调用可能的空指针风险
- **[WARNING] Java-MemoryLeak**：检测非静态内部类可能造成的内存泄漏

#### 通用 Android 规则
- **[WARNING] Android-HardcodedUrls**：检查硬编码的 IP 地址或 URL
- **[WARNING] Android-ViewHolderPattern**：检查 ViewHolder 模式的正确使用
- **[BLOCK] Android-BinaryFiles**：阻止提交 `.apk`/`.dex`/`.aar`/`.so` 二进制文件

### AI 辅助审查

支持多种 AI 服务提供商：
- **Anthropic Claude API** - 原生支持
- **OpenRouter** - 支持调用多种模型
- **Local Ollama** - 本地部署大模型

AI 提示词支持**按项目配置**，每个项目可以定义自己特有的审查要点。

改进的 AI 解析机制：
- 使用 `<findings>...</findings>` 标签包裹结果，AI 可在外部自由输出分析过程
- 解析容错性更强，个别问题格式错误不影响整体结果
- 支持预期总数验证，方便调试解析完整性

#### AI 和本地规则开关控制

现在支持独立开关控制：
- 在图形化界面中分别提供复选框控制 AI 审查和本地规则审查开关
- 在配置文件中通过 `aiEnabled` 和 `localEnabled` 字段设置默认行为
- 禁用 AI 后，工具仅执行本地静态规则检查，扫描速度更快
- 禁用本地规则后，工具仅执行 AI 辅助审查，专注 AI 发现的问题
- 必须至少启用其中一项才能开始扫描

#### AI 输出格式新增参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `always_display` | 是否总是显示该检查项，`true` 即使未发现问题也会展示 | `false` || `severity` | 严重级别：`BLOCK`/`WARNING` | `WARNING` |

## 项目结构

```
code_review_kotlin_version/
├── gradle/                     # Gradle wrapper
├── src/
│   └── main/
│       ├── kotlin/
│       │   └── com/codereview/
│       │       ├── main/          # 主入口
│       │       ├── core/          # 核心数据结构和工具
│       │       ├── rules/         # 规则
│       │       │   ├── common/    # 通用规则
│       │       │   │   ├── java/   # Java 规则
│       │       │   └── android/  # Android 规则
│       │       ├── ai/            # AI 模块
│       │       │   └── providers/  # AI 提供商实现
│       │       ├── gui/           # Compose GUI 界面
│       │       ├── cli/           # 命令行入口
│       │       └── report/        # 报告生成
│       └── resources/
│           ├── ai_prompts/        # AI 提示词模板
│           │   ├── common/
│           │   └── projects/
│           └── ai_config/         # 默认 AI 客户端配置
├── build.gradle.kts            # Gradle 构建配置
├── settings.gradle.kts         # Gradle 设置
└── README.md
```

## 环境要求

- JDK 17 或更高版本
- Git

## 构建

```bash
# 清理并构建
./gradlew.bat clean build

# 运行 GUI
./gradlew.bat run

# 运行 CLI
./gradlew.bat run --args="--project payment"

# 打包成 Windows exe 安装包
./gradlew.bat jpackage
```

打包完成后，exe 安装包位于：`build/compose/binaries/main/jpackage/CodeReview-1.0.0.exe`

## 使用方法

### GUI 方式（推荐）

1. 双击 `CodeReview-1.0.0.exe` 安装
2. 启动后选择项目类型（收单软件/收银台软件/MIS/MTMS 设备管理）
3. 点击 **浏览...** 选择你的 Android 项目根目录
4. 选择扫描模式：
   - **全局扫描**：扫描所有文件
   - **SVN Diff 扫描**：仅扫描 SVN 变更文件
   - **Git Diff 扫描**：仅扫描 Git 变更文件
5. 可选：配置 AI 审查
   - 勾选 "启用 AI 辅助审查" 复选框（默认启用）
   - 点击 "AI 配置" 按钮可打开详细设置
6. 点击 **开始代码审查** 按钮
7. 审查完成后会显示扫描结果统计信息
8. 自动打开生成的报告文件：
   - **HTML 报告**：简洁的问题列表视图（用于快速查看）
   - **纯文本日志**：包含完整详细信息和 AI 原始响应（用于分享或存档）

### CLI 方式（用于 SVN/Git pre-commit 钩子）

```bash
# 全局扫描
CodeReview --project payment --output /path/to/output

# SVN Diff 模式（仅扫描变更文件）
CodeReview --project payment --diff-mode svn

# Git Diff 模式（仅扫描变更文件）
CodeReview --project payment --diff-mode git

# 禁用 AI 审查，仅执行本地静态规则检查
CodeReview --project payment --diff-mode git --no-ai
```

输出格式说明：
- 生成 **HTML 简洁报告**：用于快速查看扫描结果
- 生成 **纯文本日志 (.log)**：包含所有问题的详细信息和 AI 原始响应（不做转义保持原样）
- 不再生成 TXT、JSON 和 Markdown 格式的报告

## AI 配置

编辑 `src/main/resources/ai_config/ai_client_config.json`：

```json
{
  "aiEnabled": true,
  "localEnabled": true,
  "provider": "openrouter",
  "apiKey": "your-api-key-here",
  "apiUrl": "https://openrouter.ai/api/v1/chat/completions",
  "model": "openai/gpt-4-turbo-preview",
  "maxTokens": 4096,
  "timeoutSeconds": 60
}
```

| 配置项 | 说明 |
|--------|------|
| `aiEnabled` | 是否启用 AI 辅助审查功能（true/false），禁用后仅执行本地静态规则检查 |
| `localEnabled` | 是否启用本地规则审查功能（true/false），禁用后仅执行 AI 辅助审查 |
| `provider` | AI 服务提供商（claude/openrouter/ollama） |
| `apiKey` | API 密钥 |
| `apiUrl` | API 端点地址 |
| `model` | 使用的模型名称 |
| `maxTokens` | 最大令牌数 |
| `timeoutSeconds` | 请求超时时间（秒） |

| 提供商 | 配置说明 |
|--------|----------|
| `claude` | Anthropic Claude API |
| `openrouter` | OpenRouter 统一开放路由 |
| `ollama` | 本地 Ollama 部署 |

## 如何新增本地规则

1. 在 `src/main/kotlin/com/codereview/rules/common/java/` 或 `android/` 新建 `.kt` 文件
2. 继承 `BaseRule` 抽象类，实现 `checkDiff` 和 `checkFullFile` 方法
3. **可选**：如果希望该规则**总是显示在报告中**（即使本次扫描没有发现问题），添加：
   ```kotlin
   override val alwaysDisplay get() = true
   ```
   这样无论是否发现问题，规则都会在 HTML 报告中展示：
   - 发现问题时正常显示问题
   - 未发现问题时显示绿色 PASS 行"未发现问题 ✓"
4. 在对应项目的 `rules.json` 中添加规则全类名

```json
{
  "enabledRules": [
    "com.codereview.rules.common.java.YourNewRule"
  ]
}
```

完成！下次构建后新规则就会被加载。

## AI 自定义审查规则

在项目自定义提示词中，可以要求 AI 按照指定格式输出，并使用 `always_display` 参数控制是否总是展示：

```
<findings>
file_path=path/to/file.java&line_start=10&line_end=20&issue_type=issue-type&severity=WARNING&message=问题描述&suggestion=修复建议&always_display=true;
total=1;
</findings>
```

参数说明：
- `file_path` - 问题文件路径
- `line_start`/`line_end` - 问题起止行号
- `issue_type` - 问题类型
- `severity` - 严重级别：`BLOCK`/`WARNING`
- `message` - 问题描述
- `suggestion` - 修复建议
- `always_display` - `true` 即使本次没有发现问题也固定显示，`false` 仅在发现问题时显示（默认）

AI 输出要求：
- 所有问题必须放在 `<findings>...</findings>` 标签内
- 每个问题以分号 `;` 结尾
- 最后一行必须是 `total=N;` 声明问题总数

