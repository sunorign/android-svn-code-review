# Code Review - Kotlin 版本

> Android 客户端自动化代码审查工具 - Kotlin + Compose Multiplatform 版本

## 项目介绍

Code Review 是一款专为 **Android 客户端开发人员** 设计的自动化代码审查工具，旨在帮助开发人员在提交代码前发现常见问题和潜在 bug，提高代码质量，减少后期代码评审成本。

这是 Kotlin 版本，使用 Gradle 构建，可以直接打包成 Windows `.exe` 可执行文件，开箱即用。

- 支持**本地静态规则检查**和 **AI 辅助审查** 双重机制，可独立开关控制
- 提供用户友好的**图形化界面**，所有设置均可在界面中完成，无需手动编辑配置文件
- **可视化规则管理**：在 GUI 中可勾选启用/禁用单个本地规则，只检查你需要的规则
- 支持三种扫描模式：全局扫描全量代码、SVN Diff 扫描变更文件、Git Diff 扫描变更文件
- Diff 模式支持两种粒度：整个文件扫描 / 仅扫描变更行
- Diff 模式仅扫描修改过的文件，扫描速度更快
- 支持 GUI 双击启动，也支持 **CLI 命令行** 集成到 SVN/Git pre-commit 钩子
- 生成 **HTML 简洁报告**（用于浏览器快速查看）和 **Markdown 完整报告**（用于存档分享）
- 支持多种 AI 服务提供商：Anthropic Claude API、OpenRouter、本地 Ollama
- 改进的 AI 解析算法，使用标签包裹格式，大幅提高解析成功率
- 支持 `alwaysDisplay` 固定显示规则，即使未发现问题也会在报告中展示为绿色 PASS
- 所有设置持久化保存，重启后自动恢复

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

#### Diff 粒度

Diff 模式支持两种扫描粒度：
- **整个文件**：对变更文件进行完整扫描，检查更全面
- **仅变更行**：只扫描被修改的代码行，扫描速度更快

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
| `always_display` | 是否总是显示该检查项，`true` 即使未发现问题也会展示 | `false` |
| `severity` | 严重级别：`BLOCK`/`WARNING` | `WARNING` |

### AI 审查工作原理

v2.2 采用了 **分层提示词架构 + 基于标签的智能检索**，既结构清晰易于维护，又能动态控制提示词长度减少幻觉：

```
┌─────────────────────────────────────────────────────────────┐
│  System Prompt   - 固定输出格式规则，永远不变                  │
│  Task Prompt    - 按扫描模式不同（Diff/Global）给出任务指导    │
│  RuleDoc        - 每条审查规则独立知识文档（含标签）            │
│  Code Input     - 待审查代码内容                              │
└─────────────────────────────────────────────────────────────┘
```

**工作流程：**

1. **加载配置**：从 `~/.code-review/ai_config.json` 加载 AI 配置（API Key、模型、URL 等）
2. **加载规则文档**：
   - 首先加载内置规则文档（`src/main/resources/ai_rules/`），每条规则包含标签
   - 然后加载用户自定义规则文档（`~/.code-review/rule-docs/`），覆盖同名规则
3. **关键词分析**（标签检索启用时）：
   - `QueryAnalyzer` 分析待审查代码，提取关键词
   - 支持驼峰命名（`debugLog` → `debug`, `log`）和下划线命名（`debug_log` → `debug`, `log`）拆分
   - 自动过滤 Java/Kotlin 关键字和过短单词（< 2 字符）
   - 输出去重后的小写关键词列表
4. **规则过滤**：
   - 启用标签检索：只保留关键词与规则标签有交集的规则
   - 禁用标签检索：保留所有规则（兼容原有行为）
5. **组装提示词**：`PromptAssembler` 将四层提示词组装为最终发送给 AI 的提示词
6. **调用 API**：根据配置的提供商调用对应的 AI 服务
7. **解析结果**：AI 返回结果后，从 `<findings>...</findings>` 标签中提取问题列表，填充元数据
8. **生成报告**：将 AI 发现的问题和本地规则发现的问题合并，生成 HTML + Markdown 双报告，元数据展示在报告中

**为什么这样设计：**

- ✅ **易于维护**：每条规则一个 Markdown 文件，新增/修改规则直接编辑文件即可，不需要改代码
- ✅ **支持扩展**：用户可以在 `~/.code-review/rule-docs/` 添加自定义规则，不需要重新编译
- ✅ **智能裁剪**：标签检索只注入和当前代码相关的规则，大幅缩短提示词长度
- ✅ **减少幻觉**：避免不相关规则干扰 AI 判断，提高结果准确性
- ✅ **降低成本**：更短的提示词意味着更少的 token 消耗，降低 API 调用费用
- ✅ **向后兼容**：输出协议完全不变，可以随时开关标签检索功能

**标签检索工作原理：**

每条 RuleDoc 在文档开头声明标签：
```markdown
# 标签
debug, log, logging, java
```

### 匹配流程：

```
┌─────────────────────────────────────────────────────────────┐
│  1. 提取关键词：从待审查代码中提取所有标识符                       │
│     - 使用正则表达式匹配所有标识符                                 │
│     - 驼峰命名 (debugLog) → 拆分为 debug + log                     │
│     - 下划线命名 (debug_log) → 拆分为 debug + log                   │
│     - 自动过滤 Java/Kotlin 关键字 (if/else/class/fun 等)            │
│     - 过滤过短单词，返回去重后的小写关键词集合                        │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 规则匹配：检查每个 RuleDoc 的标签与关键词是否有交集             │
│     val matches = extractedKeywords.intersect(ruleTags).size   │
│     匹配数量 ≥ 1 → 保留该规则                                     │
│     匹配数量 = 0 → 过滤掉该规则                                   │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 组装提示词：只将匹配上的规则注入最终提示词                     │
└─────────────────────────────────────────────────────────────┘
```

**示例：** 当代码中包含很多 `Log.d("debug", ...)` 调试语句时：
1. 提取出关键词：`debug`, `log`, `logging`
2. 匹配规则标签：所有包含 `debug`/`log` 标签的规则保留
3. 结果：只有和日志调试相关的规则被注入，其他不相关规则被跳过

**优势：**
- 提示词长度缩短 **30% ~ 70%**
- 减少不相关规则带来的干扰，**降低 AI 幻觉**
- 更少的 token 消耗，**降低 API 调用费用**
- 响应速度更快

### 语义检索（RAG）工作原理

当启用**语义检索**模式（需要 Ollama 提供商），系统会：

```
┌─────────────────────────────────────────────────────────────┐
│  1. 预计算：应用启动时为每条 RuleDoc 计算 embedding 向量      │
│     - 结果缓存到内存，整个应用生命周期只计算一次                 │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 查询编码：对本次待审查代码计算 embedding 向量              │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 相似度计算：计算查询向量与每条 RuleDoc 向量的余弦相似度      │
│     cos(a, b) = (a · b) / (||a|| * ||b||)                     │
│     相似度范围 [-1, 1]，值越大越相似                             │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 返回 top-N：按相似度降序排序，返回最相关的 N 条规则          │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. 组装提示词：只将最相似的 N 条规则注入最终提示词              │
└─────────────────────────────────────────────────────────────┘
```

**相比标签匹配的优势：**
- 关键词匹配只能匹配**字面相同**的词汇
- 语义检索可以匹配**语义相近**但字面不同的内容
- 例如：代码中有 `SharedPreferences`，语义检索能匹配到 `persistence`/`storage`/`data` 相关规则

**当前限制：**
- 目前仅支持 Ollama 本地 embedding
- 预计算在启动时进行，启动时间会略有增加（取决于规则数量）
- 缓存存储在内存，重启后重新计算

### AI 自定义规则添加（自定义审查规则）

你可以在 `~/.code-review/rule-docs/` 目录添加自定义审查规则，文件格式为 Markdown。工具会自动加载这些规则，并根据检索模式（标签匹配/语义检索）动态注入到 AI 提示词中。

**格式要求：**

每个规则文件 `.md` 必须包含以下 sections：

```markdown
# 规则名
Kotlin-UnusedImports

# 标签
kotlin,import,clean-code

# 规则描述
检测代码中未使用的 import 语句，这些语句会增加编译时间并影响代码可读性。

# 问题示例
```kotlin
import android.view.View
import kotlin.coroutines.CoroutineContext  // 未使用

class MyClass {
    fun doSomething() {
        // ... 使用了 View 但没使用 CoroutineContext
    }
}
# 修复建议
删除未使用的 import 语句，可以使用 IDE 的 "Optimize Imports" 功能自动清理。
```

**各 section 说明：**

| Section      | 说明                                     | 必填                   |
| ------------ | ---------------------------------------- | ---------------------- |
| `# 规则名`   | 规则的唯一名称                           | ✅ 必填                 |
| `# 标签`     | 逗号分隔的标签列表，用于标签检索         | ✅ 必填（至少一个标签） |
| `# 规则描述` | 描述这条规则要检查什么问题               | ✅ 必填                 |
| `# 问题示例` | 给出一个违反规则的代码示例，帮助 AI 理解 | ✅ 推荐                 |
| `# 修复建议` | 说明应该如何修复这个问题                 | ✅ 推荐                 |

**标签的作用：**
- 标签匹配模式下，只有当提取的关键词与规则标签有交集时，规则才会被注入提示词
- 语义检索模式下，标签会帮助 embedding 更好理解规则主题
- 建议标签：语言（`java`/`kotlin`/`android`） + 领域（`memory`/`security`/`performance`） + 具体问题（`debug`/`log`/`leak`）

**工作流程：**
1. 工具启动时，扫描 `~/.code-review/rule-docs/` 目录下所有 `.md` 文件
2. 解析每个文件，转换为 `RuleDoc` 对象
3. 如果文件名和内置规则重名，用户自定义规则会**覆盖**内置规则
4. 检索时，根据标签匹配或语义检索选择相关规则注入提示词

因此，你可以：
- **添加新规则**：新增 `.md` 文件即可
- **修改内置规则**：在用户目录添加同名文件覆盖内置规则
- **删除规则**：删除用户目录中的文件即可（如果是内置规则不会被删除，只是用户自定义被删除）

### 支持的 AI 提供商

| 提供商               | 说明                                                         | 需要配置                              |
| -------------------- | ------------------------------------------------------------ | ------------------------------------- |
| **Anthropic Claude** | 直接使用 Anthropic 官方 API                                  | API Key                               |
| **OpenRouter**       | 通过 OpenRouter 访问多种模型（GPT-4、Claude、Minimax、通义千问等） | API Key                               |
| **Ollama**           | 本地部署开源大模型（Llama 2、Mistral 等）                    | 不需要 API Key，只需要本地运行 Ollama |

## 项目结构

code_review_kotlin_version/
├── gradle/                               # Gradle wrapper
├── src/
│   └── main/
│       ├── kotlin/com/codereview/
│       │   ├── main/                    # 主入口（自动判断 GUI/CLI）
│       │   ├── core/                    # 核心数据结构和扫描工具
│       │   ├── rules/                   # 规则加载和管理
│       │   │   ├── common/              # 通用规则
│       │   │   │   ├── java/            # Java 通用规则
│       │   │   │   └── android/         # Android 通用规则
│       │   ├── ai/                      # AI 模块
│       │   │   ├── providers/           # AI 提供商实现
│       │   │   ├── EmbeddingClient.kt   # Embedding 客户端接口 + Ollama 实现
│       │   │   ├── SemanticMatcher.kt   # 语义相似度匹配（余弦相似度）
│       │   │   ├── QueryAnalyzer.kt     # 代码关键词分析器（标签检索）
│       │   │   ├── RuleDoc.kt           # RuleDoc 数据类（规则知识文档，含 embedding 缓存）
│       │   │   ├── AiFinding.kt         # AI 发现结果 + FindingMetadata
│       │   │   ├── AiReviewContext.kt   # AI 审查上下文
│       │   │   ├── RuleDocLoader.kt     # RuleDoc 加载器（内置 + 用户自定义）
│       │   │   ├── PromptAssembler.kt   # 分层提示词组装器（支持三种检索模式）
│       │   │   └── AiConfig.kt          # AI 配置（含检索模式设置）
│       │   ├── gui/                     # Compose 图形界面
│       │   ├── cli/                     # 命令行入口
│       │   └── report/                  # 报告生成
│       └── resources/
│           ├── ai_rules/                 # AI RuleDoc 规则知识文档
│           │   ├── system-prompt.md     # System Prompt（固定格式规则）
│           │   ├── task-diff.md         # Task Prompt（Diff 模式任务说明）
│           │   ├── task-global.md       # Task Prompt（Global 模式任务说明）
│           │   ├── common/              # 通用规则
│           │   │   ├── java/            # Java 通用规则文档
│           │   │   └── android/         # Android 通用规则文档
│           ├── ai_prompts/              # 兼容保留：原提示词模板（已迁移）
│           │   └── common/              # 通用提示词
│           └── ai_config/               # AI 客户端默认配置
├── docs/
│   └── superpowers/
│       ├── plans/                       # 实施计划
│       └── specs/                       # 设计规格
├── build.gradle.kts          # Gradle 构建配置
├── settings.gradle.kts       # Gradle 项目设置
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

1. 双击 `CodeReview-1.0.0.exe` 安装启动
2. 右上角提供三个设置按钮：
   - **扫描设置**：选择扫描模式和 Diff 粒度
   - **本地设置**：可视化启用/禁用单个本地规则，独立开关本地规则审查
   - **AI 设置**：配置 AI 提供商、API Key、模型参数，独立开关 AI 审查
3. 点击 **浏览...** 选择你的 Android 项目根目录
4. 点击 **开始代码审查** 按钮
5. 审查完成后会显示扫描结果统计信息
6. 自动在浏览器中打开生成的 HTML 报告：
   - **HTML 报告**：美观的问题列表视图，方便快速查看
   - **Markdown 报告**：包含完整详细信息和 AI 调试信息，用于存档分享

**扫描设置说明**：
- **扫描模式**：全局扫描（全量代码）/ SVN Diff（仅变更文件）/ Git Diff（仅变更文件）
- **Diff 粒度**：整个文件（扫描整个变更文件）/ 仅变更行（只扫描修改的行，速度更快）
- **输出目录**：可自定义报告保存目录，默认 `~/code-review-output`，勾选"使用默认路径"或自定义选择

### CLI 方式（用于 SVN/Git pre-commit 钩子）

```bash
# 全局扫描
CodeReview --output /path/to/output

# SVN Diff 模式（仅扫描变更文件）
CodeReview --diff-mode svn

# Git Diff 模式（仅扫描变更文件）
CodeReview --diff-mode git

# 禁用 AI 审查，仅执行本地静态规则检查
CodeReview --diff-mode git --no-ai
```

> **说明**：`--project` 参数保留但已不再使用，规则启用状态统一从本地设置加载

输出格式说明：
- 生成 **HTML 简洁报告**：美观的问题列表视图，直接在浏览器中打开查看
- 生成 **Markdown 完整报告**：包含所有问题的详细信息和 AI 调试信息，便于存档分享

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
  "timeoutSeconds": 60,
  "retrievalMode": "TAG_MATCHING",
  "semanticTopN": 10
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
| `retrievalMode` | 规则检索模式：`NONE`(不检索，全注入) / `TAG_MATCHING`(标签匹配，默认) / `SEMANTIC`(语义检索，需要 Ollama) |
| `semanticTopN` | 语义检索返回最相关规则数量，默认 10 |

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

完成！下次构建后新规则就会被自动发现，并出现在 GUI 的"本地设置"对话框中，你可以勾选启用或禁用。

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

## 最近更新

### v2.3 - Phase 3 完成 - RAG 语义检索增强

- ✅ **Ollama Embedding 支持**：使用 Ollama 本地生成 embedding 向量，无需额外费用
- ✅ **预计算缓存**：启动时预计算所有 RuleDoc  embedding，缓存到内存
- ✅ **余弦相似度匹配**：计算输入代码与规则语义相似度，返回最相关规则
- ✅ **可配置 top-N**：可自定义返回最相关的规则数量（默认 10）
- ✅ **三种检索模式可选**：不启用检索 / 标签匹配 / 语义检索
- ✅ **完整向后兼容**：回退机制完善，非 Ollama 提供商自动回退到标签匹配
- ✅ **优势**：相比标签匹配，能匹配语义相近但字面不同的内容，匹配精度更高

### v2.2 - Phase 2 完成 - 标签检索 + Metadata 输出

- ✅ **QueryAnalyzer 代码关键词分析**：自动分析代码提取关键词，支持驼峰/下划线命名拆分
- ✅ **基于标签的规则检索**：只注入与当前代码相关的规则，大幅缩短提示词长度
- ✅ **FindingMetadata 元数据**：AI 发现结果关联来源规则信息，报告中展示规则名称
- ✅ **GUI 可配置开关**：AI 设置中新增检索模式选择，标签匹配默认开启
- ✅ **完整向后兼容**：禁用标签检索时完全保持原有行为，metadata 为空不影响报告显示
- ✅ **收益**：提示词缩短 30% ~ 70%，减少幻觉，降低 token 消耗，提高响应速度

### v2.1 - AI Prompt 架构升级 - 分层提示词 + RuleDoc 知识体系

- ✅ **Prompt 分层架构**：按职责隔离为 System / Task / RuleDoc / Code 四层
  - System Prompt：固定输出格式规则，永远不变
  - Task Prompt：按扫描模式不同（Diff/Global）给出不同任务指导
  - RuleDoc：每条审查规则独立知识文档，分层清晰
  - Code Input：待审查代码内容
- ✅ **RuleDoc 独立存储**：每个规则一个 Markdown 文件，便于维护
- ✅ **支持用户自定义 RuleDoc**：可在 `~/.code-review/rule-docs/` 添加自定义规则，无需重新编译
- ✅ **PromptAssembler**：统一组装入口，为未来 RAG 演进预留接口
- ✅ **向后兼容**：输出协议完全不变，不影响现有解析和报告生成

### v2.0 - 架构重构 - 图形化设置界面

- ✅ **架构重构**：移除按项目分类管理，改为统一图形化管理所有规则
- ✅ **GUI 新增三个设置对话框**：
  - 扫描设置：可视化选择扫描模式和 Diff 粒度
  - 本地规则设置：勾选启用/禁用单个规则，独立开关本地规则审查
  - AI 设置：界面化配置所有 AI 参数，无需手动编辑 JSON
- ✅ **所有设置持久化**：配置保存后重启自动恢复，无需重复设置
- ✅ **支持独立开关**：AI 审查和本地规则审查可分别启用/禁用，满足不同场景需求
- ✅ **报告格式优化**：同时输出 HTML（快速查看）和 Markdown（完整存档）两种格式
- ✅ **支持自定义输出目录**：GUI 中可选择报告保存目录，设置持久化保存

---

## 后续改造计划

本项目采用增量演进方式，当前已完成 **Phase 3**。

### ✅ Phase 1 - 分层提示词架构升级 （完成）

- 按职责隔离为 System / Task / RuleDoc / Code 四层架构
- RuleDoc 独立存储，每条规则一个 Markdown 文件
- 支持用户自定义 RuleDoc，无需重新编译

### ✅ Phase 2 - 标签检索 + Metadata 输出 （完成）

- QueryAnalyzer 分析代码提取关键词
- 基于标签交集匹配只注入相关规则，缩短提示词长度 30% ~ 70%
- FindingMetadata 存储来源规则信息，报告中展示
- GUI 可配置开关，默认开启

### ✅ Phase 3 - RAG 语义检索增强 （完成）

- Ollama Embedding 支持：使用 Ollama 本地生成 embedding 向量，无需额外费用
- 预计算缓存：启动时预计算所有 RuleDoc embedding，缓存到内存
- 余弦相似度匹配：计算输入代码与规则语义相似度，返回最相关规则
- 可配置 top-N：自定义返回最相关的规则数量（默认 10）
- 三种检索模式可选：不启用检索 / 标签匹配 / 语义检索

### ⏳ Phase 4 - 未来改进方向 （计划中）

**可能的改进方向：**
1. 支持 Anthropic/OpenAI 远程 embedding API
2. 持久化 embedding 缓存到磁盘，避免每次启动重新计算
3. 混合检索：标签匹配 + 语义检索结合
4. 支持向量数据库（当规则数量非常大时）

---

**如何开始后续改造：**
1. 阅读设计文档：`docs/ai_prompt_architecture_design.md`
2. 阅读已完成的 Phase 1/2/3 实现：`src/main/kotlin/com/codereview/ai/`
3. 使用 `superpowers:brainstorming` → `superpowers:writing-plans` → `superpowers:subagent-driven-development` 流程进行开发

