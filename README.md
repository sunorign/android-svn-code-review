# Code Review - Kotlin Version

[English](README.md) | [简体中文](README.zh-CN.md)

> Automated Code Review Tool for Android Clients - Kotlin + Compose Multiplatform Version

---

## Introduction

Code Review is an automated code review tool designed specifically for **Android client developers**. It helps developers identify common issues and potential bugs before committing code, improves code quality, and reduces code review costs later.

This is the Kotlin version, built with Gradle, and can be directly packaged into a Windows `.exe` executable, ready to use out of the box.

- Supports **local static rule checking** and **AI-assisted review** dual mechanism, with independent toggle control
- Provides a user-friendly **graphical interface**, all settings can be completed in the interface without manually editing configuration files
- **Visual rule management**: In GUI, you can check to enable/disable individual local rules, only check the rules you need
- Supports three scanning modes: global scan of all code, SVN Diff scan of changed files, Git Diff scan of changed files
- Diff mode supports two granularities: entire file scan / only changed lines scan
- In Diff mode, only modified files are scanned, faster scanning speed
- Supports GUI double-click startup, also supports **CLI command line** integration into SVN/Git pre-commit hooks
- Generates **concise HTML report** (for quick viewing in browser) and **complete Markdown report** (for archiving and sharing)
- Supports multiple AI service providers: Anthropic Claude API, OpenRouter, local Ollama
- Improved AI parsing algorithm, uses tags to wrap format, greatly improves parsing success rate
- Supports `alwaysDisplay` fixed display rule, even if no problems are found, it will be displayed as green PASS in the report
- All settings are persistently saved and automatically restored after restart

## Features

### Scan Modes

Code Review provides three scanning modes to meet different scenarios:

#### Global Scan
- Scans all source files in the project
- Suitable for comprehensive code review after initial use or major refactoring
- Most comprehensive inspection, but longer scanning time

#### SVN Diff Mode
- Only scans **modified files** in SVN version control
- Requires SVN environment configuration
- Fast scanning speed, suitable for incremental code review in daily development

#### Git Diff Mode
- Only scans **modified files** in Git version control
- Requires Git environment configuration
- Fast scanning speed, suitable for incremental code review in daily development

> **Tip**: Diff mode (SVN or Git) only checks changed files, which significantly improves speed compared to global scan, and is the recommended usage for daily development.

#### Diff Granularity

Diff mode supports two scanning granularities:
- **Entire file**: Full scan of the changed file, more comprehensive inspection
- **Changed lines only**: Only scans the modified code lines, faster scanning speed

### Local Static Rule Checking

#### Severity Level Description

| Level | Color | Description |
|-------|-------|-------------|
| BLOCK | Red | Issues that must be fixed |
| WARNING | Yellow | Issues that need attention |

#### Always Display Rule

For important rules, you can set `alwaysDisplay = true`, so even if **no problems are found** in this scan, an additional green PASS line will be added to the HTML report:

| Priority | Rule Name | Location | Issue Description | Code Snippet |
|----------|-----------|----------|-------------------|--------------|
| PASS | Java-DebugLogging | - | No issues found ✓ | - |

#### General Java Rules
- **[BLOCK] Java-DebugLogging**: Checks `System.out.println` and `Log.d`/`Log.v` debug logs
- **[BLOCK] Java-HardcodedSecrets**: Detects hardcoded sensitive information such as passwords, keys, API Keys
- **[WARNING] Java-UnclosedResources**: Checks for unclosed Cursor/Stream/Connection resources
- **[WARNING] Java-NPERisk**: Identifies potential null pointer risks in multi-level calls
- **[WARNING] Java-MemoryLeak**: Detects memory leaks caused by non-static inner classes

#### General Android Rules
- **[WARNING] Android-HardcodedUrls**: Checks for hardcoded IP addresses or URLs
- **[WARNING] Android-ViewHolderPattern**: Checks for correct usage of ViewHolder pattern
- **[BLOCK] Android-BinaryFiles**: Prevents submission of `.apk`/`.dex`/`.aar`/`.so` binary files

### AI-Assisted Review

Supports multiple AI service providers:
- **Anthropic Claude API** - Native support
- **OpenRouter** - Supports calling multiple models
- **Local Ollama** - Locally deployed large model

Improved AI parsing mechanism:
- Uses `<findings>...</findings>` tags to wrap results, AI can freely output analysis process outside
- Stronger parsing fault tolerance, individual format errors do not affect the overall result
- Supports expected total count verification, convenient for debugging parsing integrity

#### AI and Local Rule Toggle Control

Now supports independent toggle control:
- Provides separate checkboxes in the graphical interface to control AI review and local rule review switches
- Sets default behavior through `aiEnabled` and `localEnabled` fields in the configuration file
- After disabling AI, the tool only performs local static rule checking, faster scanning speed
- After disabling local rules, the tool only performs AI-assisted review, focusing on issues found by AI
- At least one must be enabled to start scanning

#### New Parameters in AI Output Format

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `always_display` | Whether to always display this check item, `true` displays even if no issues found | `false` |
| `severity` | Severity level: `BLOCK`/`WARNING` | `WARNING` |

### How AI Review Works

v2.2 adopts **layered prompt architecture + tag-based intelligent retrieval**, which is structurally clear and easy to maintain, and can dynamically control prompt length to reduce hallucinations:


```
┌──────────────────────────────────────────────────────────────────┐
│  System Prompt   - Fixed output formatting rules, never changes  │
│  Task Prompt    - Task guidance based on scan mode (Diff/Global)  │
│  RuleDoc        - Each review rule has an independent knowledge   │
│                 document (with tags)                              │
│  Code Input     - Code content to be reviewed                    │
└──────────────────────────────────────────────────────────────────┘
```

**Workflow:**



1. **Load configuration**: Load AI configuration (API Key, model, URL, etc.) from `~/.code-review/ai_config.json`
2. **Load rule documents**:
   - First load built-in rule documents (`src/main/resources/ai_rules/`), each rule contains tags
   - Then load user-defined rule documents (`~/.code-review/rule-docs/`), overwriting rules with the same name
3. **Keyword analysis** (when tag retrieval is enabled):
   - `QueryAnalyzer` analyzes the code to be reviewed and extracts keywords
   - Supports camelCase (`debugLog` → `debug`, `log`) and snake_case (`debug_log` → `debug`, `log`) splitting
   - Automatically filters Java/Kotlin keywords and words that are too short (< 2 characters)
   - Outputs a deduplicated list of lowercase keywords
4. **Rule filtering**:
   - When tag retrieval is enabled: only retain rules where keywords intersect with rule tags
   - When tag retrieval is disabled: retain all rules (compatible with original behavior)
5. **Assemble prompt**: `PromptAssembler` assembles the four-layer prompts into the final prompt sent to AI
6. **Call API**: Call the corresponding AI service according to the configured provider
7. **Parse results**: After AI returns the result, extract the problem list from the `<findings>...</findings>` tag and fill in metadata
8. **Generate report**: Merge issues found by AI and local rules, generate HTML + Markdown dual reports, metadata is displayed in the report

**Why this design:**

- ✅ **Easy to maintain**: One Markdown file per rule, you can add/modify rules by directly editing the file without changing code
- ✅ **Extensible**: Users can add custom rules in `~/.code-review/rule-docs/` without recompilation
- ✅ **Smart cropping**: Tag retrieval only injects rules related to the current code, greatly shortening prompt length
- ✅ **Reduced hallucination**: Avoids interference from irrelevant rules to AI judgment, improves result accuracy
- ✅ **Cost reduction**: Shorter prompts mean less token consumption, lower API call costs
- ✅ **Backward compatible**: Output protocol remains completely unchanged, you can toggle tag retrieval function at any time

**How tag retrieval works:**

Each RuleDoc declares tags at the beginning of the document:
```markdown
# Tags
debug, log, logging, java
```

### Matching Process:


```
┌──────────────────────────────────────────────────────────────────┐
│  1. Extract keywords: Extract all identifiers from the code    │
│     to be reviewed                                              │
│     - Uses regular expressions to match all identifiers           │
│     - camelCase (debugLog) → split into debug + log            │
│     - snake_case (debug_log) → split into debug + log          │
│     - Automatically filters Java/Kotlin keywords                │
│       (if/else/class/fun, etc.)                                │
│     - Filters too short words, returns deduplicated lowercase   │
│       keyword set                                              │
└──────────────────────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────────────┐
│  2. Rule matching: Check if there is an intersection between    │
│     each RuleDoc's tags and keywords                            │
│     val matches = extractedKeywords.intersect(ruleTags).size   │
│     Number of matches ≥ 1 → keep the rule                       │
│     Number of matches = 0 → filter out the rule                │
└──────────────────────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────────────┐
│  3. Assemble prompt: Only inject matched rules into the final  │
│     prompt                                                      │
└──────────────────────────────────────────────────────────────────┘
```

**Example:** When the code contains many `Log.d("debug", ...)` debug statements:
1. Extract keywords: `debug`, `log`, `logging`
2. Match rule tags: All rules containing `debug`/`log` tags are retained
3. Result: Only rules related to log debugging are injected, other irrelevant rules are skipped

**Advantages:**
- Prompt length shortened by **30% ~ 70%**
- Reduces interference from irrelevant rules, **reduces AI hallucination**
- Less token consumption, **lower API call costs**
- Faster response speed

### How Semantic Retrieval (RAG) Works

When **semantic retrieval** mode is enabled (requires Ollama provider), the system will:


```
┌──────────────────────────────────────────────────────────────────┐
│  1. Pre-computation: When the app starts, compute embedding     │
│     vector for each RuleDoc                                     │
│     - Results are cached in memory, only computed once          │
│       throughout the application lifecycle                     │
└──────────────────────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────────────┐
│  2. Query encoding: Compute embedding vector for the current   │
│     code to be reviewed                                         │
└──────────────────────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────────────┐
│  3. Similarity calculation: Compute cosine similarity between   │
│     query vector and each RuleDoc vector                        │
│     cos(a, b) = (a · b) / (||a|| * ||b||)                     │
│     Similarity ranges from [-1, 1], larger value means more      │
│       similar                                                  │
└──────────────────────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────────────┐
│  4. Return top-N: Sort by similarity in descending order,       │
│     return the top N most relevant rules                        │
└──────────────────────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────────────┐
│  5. Assemble prompt: Only inject the N most similar rules       │
│     into the final prompt                                       │
└──────────────────────────────────────────────────────────────────┘
```

**Advantages compared to tag matching:**
- Keyword matching can only match **literally identical** vocabulary
- Semantic retrieval can match **semantically similar** content with different literal expressions
- For example: code contains `SharedPreferences`, semantic retrieval can match rules related to `persistence`/`storage`/`data`

**Current limitations:**
- Currently only supports Ollama local embedding
- Pre-computation is performed at startup, startup time will increase slightly (depending on the number of rules)
- Cache is stored in memory, recalculated after restart

### Adding Custom AI Rules (Custom Review Rules)

You can add custom review rules in the `~/.code-review/rule-docs/` directory, the file format is Markdown. The tool will automatically load these rules and dynamically inject them into the AI prompt according to the retrieval mode (tag matching/semantic retrieval).

**Format requirements:**

Each `.md` rule file must contain the following sections:

```markdown
# Rule Name
Kotlin-UnusedImports

# Tags
kotlin,import,clean-code

# Description
Detect unused import statements in code, these increase compilation time and affect code readability.

# Example of Issue
```kotlin
import android.view.View
import kotlin.coroutines.CoroutineContext  // Unused

class MyClass {
    fun doSomething() {
        // ... uses View but not CoroutineContext
    }
}
```
# Fix Suggestion
Delete unused import statements, you can use IDE's "Optimize Imports" function to automatically clean up.


**Section descriptions:**

| Section      | Description                                     | Required               |
| ------------ | ----------------------------------------------- | ---------------------- |
| `# Rule Name`| Unique name of the rule                         | ✅ Required            |
| `# Tags`     | Comma-separated list of tags for tag retrieval  | ✅ Required (at least one tag) |
| `# Description` | Describe what issue this rule checks          | ✅ Required            |
| `# Example of Issue` | Give a code example that violates the rule to help AI understand | ✅ Recommended |
| `# Fix Suggestion` | Explain how to fix this issue                | ✅ Recommended |

**Role of tags:**
- In tag matching mode, the rule will only be injected into the prompt when extracted keywords intersect with the rule tags
- In semantic retrieval mode, tags help embedding better understand the rule topic
- Recommended tags: language (`java`/`kotlin`/`android`) + domain (`memory`/`security`/`performance`) + specific issue (`debug`/`log`/`leak`)

**Workflow:**
1. When the tool starts, scan all `.md` files in the `~/.code-review/rule-docs/` directory
2. Parse each file and convert it to a `RuleDoc` object
3. If the filename matches a built-in rule, the user-defined rule will **override** the built-in rule
4. During retrieval, select relevant rules to inject into the prompt based on tag matching or semantic retrieval

Therefore, you can:
- **Add new rules**: Just add a new `.md` file
- **Modify built-in rules**: Add a file with the same name in the user directory to override the built-in rule
- **Delete rules**: Delete the file in the user directory (if it's a built-in rule, it won't be deleted, only the user custom is deleted)

### Supported AI Providers

| Provider               | Description                                                         | Configuration Required                      |
| ---------------------- | ------------------------------------------------------------------- | ------------------------------------------- |
| **Anthropic Claude**   | Direct use of Anthropic official API                                | API Key                                     |
| **OpenRouter**         | Access multiple models through OpenRouter (GPT-4, Claude, Minimax, Tongyi Qianwen, etc.) | API Key |
| **Ollama**             | Locally deployed open source large model (Llama 2, Mistral, etc.)   | No API Key required, only need to run Ollama locally |

## Project Structure

```
code_review_kotlin_version/
├── gradle/                               # Gradle wrapper
├── src/
│   └── main/
│       ├── kotlin/com/codereview/
│       │   ├── main/                    # Main entry (auto-detect
│       │   │                              GUI/CLI)
│       │   ├── core/                    # Core data structures and
│       │   │                              scanning tools
│       │   ├── rules/                   # Rule loading and management
│       │   │   ├── common/              # Common rules
│       │   │   │   ├── java/            # Java common rules
│       │   │   │   └── android/         # Android common rules
│       │   ├── ai/                      # AI module
│       │   │   ├── providers/           # AI provider implementations
│       │   │   ├── EmbeddingClient.kt   # Embedding client interface
│       │   │                              + Ollama implementation
│       │   │   ├── SemanticMatcher.kt   # Semantic similarity matching
│       │   │                              (cosine similarity)
│       │   │   ├── QueryAnalyzer.kt     # Code keyword analyzer
│       │   │                              (tag retrieval)
│       │   │   ├── RuleDoc.kt           # RuleDoc data class (rule
│       │   │                              knowledge doc, with embedding
│       │   │                              cache)
│       │   │   ├── AiFinding.kt         # AI finding result +
│       │   │                              FindingMetadata
│       │   │   ├── AiReviewContext.kt   # AI review context
│       │   │   ├── RuleDocLoader.kt     # RuleDoc loader (built-in +
│       │   │                              user custom)
│       │   │   ├── PromptAssembler.kt   # Layered prompt assembler
│       │   │                              (supports three retrieval
│       │   │                              modes)
│       │   │   └── AiConfig.kt          # AI configuration (includes
│       │   │                              retrieval mode settings)
│       │   ├── gui/                     # Compose graphical interface
│       │   ├── cli/                     # Command line entry
│       │   └── report/                  # Report generation
│       └── resources/
│           ├── ai_rules/                 # AI RuleDoc rule knowledge
│           │                              documents
│           │   ├── system-prompt.md     # System Prompt (fixed format
│           │   │                              rules)
│           │   ├── task-diff.md         # Task Prompt (Diff mode task
│           │   │                              description)
│           │   ├── task-global.md       # Task Prompt (Global mode task
│           │   │                              description)
│           │   ├── common/              # Common rules
│           │   │   ├── java/            # Java common rule documents
│           │   │   └── android/         # Android common rule documents
│           ├── ai_prompts/              # Compatibility retained:
│           │                              original prompt templates
│           │                              (migrated)
│           │   └── common/              # Common prompts
│           └── ai_config/               # Default AI client configuration
├── docs/
│   └── superpowers/
│       ├── plans/                       # Implementation plans
│       └── specs/                       # Design specifications
├── build.gradle.kts          # Gradle build configuration
├── settings.gradle.kts       # Gradle project settings
└── README.md
```

## Requirements

- JDK 17 or higher
- Git

## Build

```bash
# Clean and build
./gradlew.bat clean build

# Run GUI
./gradlew.bat run

# Run CLI
./gradlew.bat run --args="--project payment"

# Package into Windows exe installer
./gradlew.bat jpackage
```

After packaging, the exe installer is located at: `build/compose/binaries/main/jpackage/CodeReview-1.0.0.exe`

## Usage

### GUI Method (Recommended)

1. Double-click `CodeReview-1.0.0.exe` to install and launch
2. Three setting buttons are provided in the upper right corner:
   - **Scan Settings**: Select scan mode and Diff granularity
   - **Local Settings**: Visually enable/disable individual local rules, independent toggle for local rule review
   - **AI Settings**: Configure AI provider, API Key, model parameters, independent toggle for AI review
3. Click **Browse...** to select your Android project root directory
4. Click **Start Code Review** button
5. After review completes, scan result statistics will be displayed
6. The generated HTML report will automatically open in the browser:
   - **HTML Report**: Beautiful issue list view, convenient for quick viewing
   - **Markdown Report**: Contains complete detailed information and AI debugging information, used for archiving and sharing

**Scan Settings Description:**
- **Scan Mode**: Global scan (full code) / SVN Diff (changed files only) / Git Diff (changed files only)
- **Diff Granularity**: Entire file (scan entire changed file) / Changed lines only (only scan modified lines, faster)
- **Output Directory**: Customizable report save directory, default `~/code-review-output`, check "Use default path" or custom selection

### CLI Method (for SVN/Git pre-commit hooks)

```bash
# Global scan
CodeReview --output /path/to/output

# SVN Diff mode (only scan changed files)
CodeReview --diff-mode svn

# Git Diff mode (only scan changed files)
CodeReview --diff-mode git

# Disable AI review, only perform local static rule checking
CodeReview --diff-mode git --no-ai
```

> **Note**: The `--project` parameter is retained but no longer used, rule enablement status is uniformly loaded from local settings

Output format description:
- Generates **concise HTML report**: Beautiful issue list view, directly open in browser for viewing
- Generates **complete Markdown report**: Contains detailed information about all issues and AI debugging information, convenient for archiving and sharing

## AI Configuration

Edit `src/main/resources/ai_config/ai_client_config.json`:

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

| Configuration | Description |
|---------------|-------------|
| `aiEnabled` | Whether to enable AI-assisted review (true/false), when disabled only local static rule checking is performed |
| `localEnabled` | Whether to enable local rule review (true/false), when disabled only AI-assisted review is performed |
| `provider` | AI service provider (claude/openrouter/ollama) |
| `apiKey` | API key |
| `apiUrl` | API endpoint address |
| `model` | Model name to use |
| `maxTokens` | Maximum tokens |
| `timeoutSeconds` | Request timeout in seconds |
| `retrievalMode` | Rule retrieval mode: `NONE`(no retrieval, inject all) / `TAG_MATCHING`(tag matching, default) / `SEMANTIC`(semantic retrieval, requires Ollama) |
| `semanticTopN` | Number of most relevant rules returned by semantic retrieval, default 10 |

| Provider | Configuration Instructions |
|----------|-----------------------------|
| `claude` | Anthropic Claude API |
| `openrouter` | OpenRouter unified open routing |
| `ollama` | Local Ollama deployment |

## How to Add Local Rules

1. Create a new `.kt` file in `src/main/kotlin/com/codereview/rules/common/java/` or `android/`
2. Inherit the `BaseRule` abstract class, implement `checkDiff` and `checkFullFile` methods
3. **Optional**: If you want this rule to **always be displayed in the report** (even if no problems are found in this scan), add:
   ```kotlin
   override val alwaysDisplay get() = true
   ```
   This way, whether problems are found or not, the rule will be displayed in the HTML report:
   - When problems are found, the problem is displayed normally
   - When no problems are found, a green PASS line "No issues found ✓" is displayed

Done! After the next build, the new rule will be automatically discovered and appear in the "Local Settings" dialog of the GUI, where you can check to enable or disable it.

## AI Custom Review Rules

In custom project prompts, you can ask AI to output in the specified format, and use the `always_display` parameter to control whether it's always displayed:

```
<findings>
file_path=path/to/file.java&line_start=10&line_end=20&issue_type=issue-type&severity=WARNING&message=Issue description&suggestion=Fix suggestion&always_display=true;
total=1;
</findings>
```

Parameter description:
- `file_path` - Path to the issue file
- `line_start`/`line_end` - Start and end line numbers of the issue
- `issue_type` - Type of issue
- `severity` - Severity level: `BLOCK`/`WARNING`
- `message` - Description of the issue
- `suggestion` - Fix suggestion
- `always_display` - `true` always displays even if no issue found this time, `false` only displays when issue found (default)

AI output requirements:
- All issues must be placed within `<findings>...</findings>` tags
- Each issue ends with a semicolon `;`
- The last line must be `total=N;` declaring the total number of issues

## Recent Updates

### v2.3 - Phase 3 Complete - RAG Semantic Retrieval Enhancement

- ✅ **Ollama Embedding Support**: Uses Ollama to locally generate embedding vectors, no additional cost
- ✅ **Precomputation Cache**: Precomputes all RuleDoc embeddings at startup, cached in memory
- ✅ **Cosine Similarity Matching**: Calculates semantic similarity between input code and rules, returns the most relevant rules
- ✅ **Configurable top-N**: Customizable number of most relevant rules to return (default 10)
- ✅ **Three retrieval modes available**: No retrieval / Tag matching / Semantic retrieval
- ✅ **Full backward compatibility**: Complete fallback mechanism, non-Ollama providers automatically fall back to tag matching
- ✅ **Advantage**: Compared to tag matching, can match content with similar semantics but different literal expressions, higher matching accuracy

### v2.2 - Phase 2 Complete - Tag Retrieval + Metadata Output

- ✅ **QueryAnalyzer Code Keyword Analysis**: Automatically analyzes code to extract keywords, supports camelCase/snake_case splitting
- ✅ **Tag-based Rule Retrieval**: Only injects rules related to current code, greatly shortening prompt length
- ✅ **FindingMetadata Metadata**: AI findings are associated with source rule information, displayed in reports
- ✅ **GUI Configurable Toggle**: Added retrieval mode selection in AI settings, tag matching enabled by default
- ✅ **Full backward compatibility**: When tag retrieval is disabled, original behavior is fully maintained, empty metadata doesn't affect report display
- ✅ **Benefits**: Prompt shortened by 30% ~ 70%, reduces hallucinations, lowers token consumption, improves response speed

### v2.1 - AI Prompt Architecture Upgrade - Layered Prompts + RuleDoc Knowledge System

- ✅ **Prompt Layered Architecture**: Isolated by responsibility into System / Task / RuleDoc / Code four layers
  - System Prompt: Fixed output formatting rules, never changes
  - Task Prompt: Different task guidance based on different scan modes (Diff/Global)
  - RuleDoc: Each review rule has an independent knowledge document, clear layering
  - Code Input: Code content to be reviewed
- ✅ **Independent Storage of RuleDoc**: One Markdown file per rule, easy to maintain
- ✅ **Supports User-defined RuleDoc**: Can add custom rules in `~/.code-review/rule-docs/`, no recompilation required
- ✅ **PromptAssembler**: Unified assembly entry, reserves interface for future RAG evolution
- ✅ **Backward compatible**: Output protocol remains completely unchanged, doesn't affect existing parsing and report generation

### v2.0 - Architecture Refactoring - Graphical Settings Interface

- ✅ **Architecture Refactoring**: Removed project-based classification management, changed to unified graphical management of all rules
- ✅ **GUI adds three settings dialogs**:
  - Scan Settings: Visually select scan mode and Diff granularity
  - Local Rule Settings: Check to enable/disable individual rules, independent toggle for local rule review
  - AI Settings: Configure all AI parameters in the interface, no need to manually edit JSON
- ✅ **All settings persistent**: Configuration is saved and automatically restored after restart, no need to repeat settings
- ✅ **Supports independent toggling**: AI review and local rule review can be enabled/disabled separately to meet different scenario needs
- ✅ **Report format optimization**: Outputs both HTML (quick viewing) and Markdown (complete archiving) formats
- ✅ **Supports custom output directory**: Can select report save directory in GUI, settings are persistently saved

---

## Future Roadmap

This project adopts incremental evolution, currently **Phase 3** is completed.

### ✅ Phase 1 - Layered Prompt Architecture Upgrade （Completed）

- Isolated into System / Task / RuleDoc / Code four-layer architecture by responsibility
- RuleDoc independent storage, one Markdown file per rule
- Supports user-defined RuleDoc, no recompilation required

### ✅ Phase 2 - Tag Retrieval + Metadata Output （Completed）

- QueryAnalyzer analyzes code to extract keywords
- Based on tag intersection matching, only injects related rules, shortens prompt length by 30% ~ 70%
- FindingMetadata stores source rule information, displayed in reports
- GUI configurable toggle, enabled by default

### ✅ Phase 3 - RAG Semantic Retrieval Enhancement （Completed）

- Ollama Embedding support: Uses Ollama to locally generate embedding vectors, no additional cost
- Precomputation cache: Precomputes all RuleDoc embeddings at startup, cached in memory
- Cosine similarity matching: Calculates semantic similarity between input code and rules, returns most relevant rules
- Configurable top-N: Customize the number of most relevant rules to return (default 10)
- Three retrieval modes available: No retrieval / tag matching / semantic retrieval

### ⏳ Phase 4 - Future Improvement Directions （Planned）

**Possible improvement directions:**
1. Support Anthropic/OpenAI remote embedding API
2. Persist embedding cache to disk, avoid recalculation on every startup
3. Hybrid retrieval: combine tag matching + semantic retrieval
4. Support vector databases (when the number of rules is very large)

---

**How to start future development:**
1. Read the design document: `docs/ai_prompt_architecture_design.md`
2. Read the completed Phase 1/2/3 implementation: `src/main/kotlin/com/codereview/ai/`
3. Use `superpowers:brainstorming` → `superpowers:writing-plans` → `superpowers:subagent-driven-development` process for development
