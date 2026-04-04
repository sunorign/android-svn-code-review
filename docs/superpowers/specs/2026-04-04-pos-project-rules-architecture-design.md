# POS 多项目场景代码审查规则架构优化设计

## 需求背景

项目团队维护 4 个 POS 相关 Android 项目：
1. **收单软件** - 专注收单，对接银行/三方支付后台
2. **收银台软件** - 业务界面，调用收单能力
3. **MIS 软件** - 通道软件，提供 WiFi/蓝牙/串口通讯
4. **MTMS** - 设备管理软件，负责更新、日志、信息上送

现有架构问题：
- `java_rules/android_rules` 分类不够清晰，文件名不能直观看出是什么语言的规则
- 所有规则全量加载，不支持按项目裁剪
- 各项目不能定义自己特有的业务规则
- Java 开发团队对 Python 项目扩展不熟悉，需要更友好的注释和文档

## 设计目标

1. 按项目分类管理规则，每个项目只加载自己需要的规则
2. 文件名命名规范，一眼看出是什么语言/平台的规则
3. GUI 支持选择项目类型，默认选中收单软件
4. 向后兼容，不影响现有命令行/SVN 钩子使用
5. 文档优化，让 Java 开发能快速上手扩展

## 架构设计

### 新目录结构

```
src/local_rules/
├── base_rule.py                    # 所有规则的抽象基类（不变）
├── __init__.py                     # 保留 load_all_rules()，新增 load_project_rules()
│
├── common_rules/                  # 通用规则池 - 各项目共享规则
│   ├── __init__.py
│   ├── java_rule_*.py             # Java 语言特有规则 → 文件名前缀 java_rule_
│   │   ├── java_rule_debug_logging.py
│   │   ├── java_rule_hardcoded_secrets.py
│   │   ├── java_rule_unclosed_resources.py
│   │   ├── java_rule_npe_risk.py
│   │   └── java_rule_memory_leak.py
│   ├── android_rule_*.py         # Android 框架特有规则 → 文件名前缀 android_rule_
│   │   ├── android_rule_hardcoded_urls.py
│   │   ├── android_rule_viewholder_pattern.py
│   │   └── android_rule_binary_files.py
│   └── kotlin_rule_*.py          # 预留 Kotlin 规则 → 文件名前缀 kotlin_rule_
│
└── pos_project_rules/             # 按项目分类 - 每个项目自己配置
    ├── __init__.py
    ├── payment/                   # 收单软件
    │   ├── __init__.py           # ← 配置本项目启用的规则
    │   └── payment_*.py          # 收单特有业务规则
    ├── cashier/                   # 收银台软件
    │   ├── __init__.py
    │   └── cashier_*.py
    ├── mis/                       # MIS 通道软件
    │   ├── __init__.py
    │   └── mis_*.py
    └── mtms/                      # MTMS 设备管理软件
        ├── __init__.py
        └── mtms_*.py
```

### 项目配置格式

每个项目目录下的 `__init__.py` 示例：

```python
"""收单软件项目 - 启用规则配置"""

# 从通用规则池导入需要的规则
from src.local_rules.common_rules.java_rule_debug_logging import DebugLoggingRule
from src.local_rules.common_rules.java_rule_hardcoded_secrets import HardcodedSecretsRule
from src.local_rules.common_rules.android_rule_hardcoded_urls import HardcodedUrlsRule

# 导入本项目特有规则
from src.local_rules.pos_project_rules.payment.payment_sensitive_keys import PaymentSensitiveKeysRule

# GUI 下拉框显示名称
PROJECT_DISPLAY_NAME = "收单软件"

# 本项目启用的规则列表 → 只加载这里列出的规则
ENABLED_RULES = [
    DebugLoggingRule(),
    HardcodedSecretsRule(),
    HardcodedUrlsRule(),
    PaymentSensitiveKeysRule(),
]
```

### GUI 界面变化

在原有界面基础上**新增项目类型下拉框**：

```
┌──────────────────────────────────┐
│  SuperPower Code Review          │
│  Android SVN 自动化代码审查工具   │
│                                  │
│  项目类型:   [收单软件 ▼]         │  ← 新增，默认选中"收单软件"
│                                  │
│  项目目录:   [........] [浏览...] │
│                                  │
│          [开始代码审查]           │
└──────────────────────────────────┘
```

### 模块交互流程

```
gui_launcher.py
    ↓
用户选择项目类型 + 项目目录
    ↓
调用 load_project_rules(project_key)
    ↓
加载项目配置的 ENABLED_RULES
    ↓
只运行这些规则 → 生成报告
```

## 代码修改点

| 文件 | 修改内容 |
|------|----------|
| `src/local_rules/__init__.py` | 新增 `load_project_rules(project_key)` 函数，读取项目配置返回 `ENABLED_RULES`；保留 `load_all_rules()` 不变 |
| `src/gui_launcher.py` | 新增项目类型下拉框，自动扫描所有项目配置；将选中项目传递给 `main.py` |
| `src/main.py` | 新增 `--project` 命令行参数；根据参数加载对应项目规则；无参数时保持原全量加载 |
| 现有规则文件 | 重命名按新命名规范；补充详细中文注释 |
| `README.md` | 整体优化，对 Java 开发者友好；补充目录结构说明；简化扩展教程 |

## 向后兼容保证

| 使用方式 | 兼容性 |
|----------|--------|
| GUI 图形界面 | 新增下拉框，默认选中收单，功能增强 |
| 原生命令行 `python src/main.py` | 不变，仍然全量加载所有规则 |
| SVN 服务端 pre-commit 钩子 | 不变，继续正常工作 |
| 环境变量支持 | 新增 `CODE_REVIEW_PROJECT` 环境变量，服务端钩子也可以按项目加载 |

## 命名规范

### 规则文件命名

| 类型 | 前缀 | 示例 |
|------|------|------|
| Java 语言规则 | `java_rule_` | `java_rule_debug_logging.py` |
| Android 框架规则 | `android_rule_` | `android_rule_hardcoded_urls.py` |
| Kotlin 语言规则 | `kotlin_rule_` | `kotlin_rule_xxx_sample.py` |
| 收单项目规则 | `payment_` | `payment_sensitive_keys.py` |
| 收银台项目规则 | `cashier_` | `cashier_ui_standard.py` |
| MIS 项目规则 | `mis_` | `mis_serial_port.py` |
| MTMS 项目规则 | `mtms_` | `mtms_version_check.py` |

## 给 Java 开发的扩展指南（会写入 README）

### 新增通用规则五步走

1. 在 `src/local_rules/common_rules/` 对应目录新建文件，按命名规范起名
2. 复制现有规则文件模板，替换内容
3. 继承 `BaseRule`，实现 4 个成员：`name`, `description`, `check_diff`, `check_full_file`
4. 如果是项目特有规则，在对应项目 `pos_project_rules/xxx/__init__.py` 的 `ENABLED_RULES` 添加你的规则
5. 测试运行 → 完成

更详细的步骤说明会放在 README 中，用 Java 开发能看懂的语言写。

## AI 提示词架构设计

### 目录结构（完全对齐本地规则）

```
src/ai_reviewer/prompt_templates/
├── common/                       # 通用提示词（兜底用）
│   ├── diff-review.md            # 默认增量审查提示词
│   └── full-review.md            # 默认全量审查提示词
└── pos_projects/                 # 各项目提示词 - 目录名完全对齐 local
    ├── payment/                 # 收单项目 ← 和 local 同名目录对齐
    │   ├── __init__.py         # 配置 ENABLED_PROMPTS（本项目启用哪些提示词）
    │   ├── sensitive-check-diff.md    # 文件名含 diff → 增量审查
    │   ├── security-audit-full.md     # 文件名含 full → 全量审查
    │   └── custom-business-rules.md   # 都不含 → 默认全量
    ├── cashier/
    ├── mis/
    └── mtms/
```

### 项目配置格式

```python
# src/ai_reviewer/prompt_templates/pos_projects/payment/__init__.py
"""收单软件项目 - AI提示词配置"""

# 本项目启用的提示词列表（文件名带 .md 后缀，一目了然）
# 自动识别规则：
# - full 权重高于 diff → 文件名同时含 full 和 diff 按 full 处理
# - 文件名包含 "diff" (大小写不敏感) → 增量审查提示词
# - 文件名包含 "full" (大小写不敏感) → 全量审查提示词
# - 都不包含 → 默认按全量审查处理
ENABLED_PROMPTS = [
    "sensitive-check-diff.md",
    "security-audit-full.md",
    "custom-business-rules.md",
]
```

### 自动识别逻辑 & 兜底策略

| 情况 | 处理方式 |
|------|----------|
| 文件名含 `diff` 不含 `full` | 识别为增量审查提示词 |
| 文件名含 `full` | 识别为全量审查提示词（权重高于 diff）|
| 文件名都不含 | 默认识别为全量审查 |
| 多个文件匹配 diff | 使用**最后一个**匹配到的 |
| 多个文件匹配 full | 使用**最后一个**匹配到的 |
| 项目没找到 diff 提示词 | 兜底使用通用 `diff-review` |
| 项目没找到 full 提示词 | 兜底使用通用 `full-review` |

### 通用提示词重命名

| 旧文件名 | 新文件名 |
|----------|----------|
| `java-diff-review.md` | `diff-review.md` |
| `android-full-review.md` | `full-review.md` |
| `kotlin-diff-review.md` | ❌ 删除 |

## 代码修改点新增

| 文件 | 修改内容 |
|------|----------|
| `src/ai_reviewer/prompt_templates/__init__.py` | 新增 `get_project_prompts(project_key)` 函数，读取项目配置，返回识别好的 diff/full 模板名 |
| `src/local_rules/__init__.py` | 新增 `list_available_projects()` 函数，供 GUI 扫描获取项目列表 |
| `src/main.py` | 根据选中项目获取对应 AI 提示词，不再硬编码 |

## 验收标准

- [ ] GUI 能看到项目类型下拉框，默认选中"收单软件"
- [ ] 选择不同项目，只加载对应项目配置的规则
- [ ] 不同项目加载对应项目配置的 AI 提示词
- [ ] 所有现有规则按新命名规范重命名完成
- [ ] 所有现有规则补充了详细中文注释
- [ ] README.md 整体优化完成，Java 开发能看懂
- [ ] 原命令行/SVN 钩子使用方式不变，向后兼容
