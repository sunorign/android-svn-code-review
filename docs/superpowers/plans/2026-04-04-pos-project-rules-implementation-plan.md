# POS 多项目规则架构优化 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构代码审查工具架构，支持按 POS 项目分类管理本地规则和 AI 提示词，每个项目只加载配置的规则和提示词，GUI 支持项目选择，对 Java 开发者更友好。

**Architecture:**
- 目录重构：`common_rules/` 放通用规则（按语言前缀命名，文件名带前缀 `java_rule_`, `android_rule_`；`pos_project_rules/项目/` 放各项目自有规则和配置。
- AI 提示词完全对齐目录结构：`prompt_templates/common/` 放通用提示词，`prompt_templates/pos_projects/项目/` 放各项目提示词，文件名自动识别 diff/full。
- 向后兼容：保留原 `load_all_rules()`，新增 `load_project_rules()`，命令行/SVN 钩子不变。

**Tech Stack:** Python 3.8+, tkinter GUI

---

## 新建/修改文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/local_rules/common_rules/__init__.py | 新建 | 空包，让 Python 识别为包 |
| `src/local_rules/java_rules/*.py → src/local_rules/common_rules/ | 重命名 | 所有现有 Java/Android 规则按新命名规范重命名，补充注释 |
| `src/local_rules/__init__.py | 修改 | 新增 `load_project_rules(project_key)`, `list_available_projects()`，保留 `load_all_rules()` |
| `src/ai_reviewer/prompt_templates/__init__.py | 新建 | 新增 `get_project_prompts(project_key)` 函数，自动识别 diff/full |
| `src/ai_reviewer/prompt_templates/common/ | 创建，重命名 | 重命名 `diff-review.md, full-review.md，删除 kotlin-diff-review.md |
| `src/ai_reviewer/prompt_templates/pos_projects/__init__.py | 新建 | 空包 |
| 创建四个项目空目录和 `__init__.py` | 新建 | payment, cashier, mis, mtms |
| `src/local_rules/pos_projects/__init__.py` | 新建 | 空包 |
| `src/gui_launcher.py | 修改 | 新增项目类型下拉框，默认选中 payment (收单软件) |
| `src/main.py | 修改 | 新增 `--project` 命令行参数，支持按项目加载规则和提示词 |
| `README.md | 修改 | 整体优化，对 Java 开发者友好，新增扩展指南 |
| 删除旧目录 | 删除 | `java_rules/, android_rules/, kotlin_rules/ 旧目录 |

---

### Task 1: 重构通用规则文件 - 重命名 + 补充注释

**Files:**
- Create: `src/local_rules/common_rules/`
- Rename: `src/local_rules/java_rules/*.py` → `src/local_rules/common_rules/java_rule_*.py`
- Rename: `src/local_rules/android_rules/*.py` → `src/local_rules/common_rules/android_rule_*.py`

- [ ] **Step 1: 创建 common_rules 目录和 __init__.py

```bash
mkdir -p src/local_rules/common_rules
```

```python
# src/local_rules/common_rules/__init__.py
"""通用规则池 - 各项目共享的通用规则
"""
```

- [ ] **Step 2: 重命名 Java 规则文件并补充头部注释

**debug_logging.py → java_rule_debug_logging.py**

```python
# src/local_rules/common_rules/java_rule_debug_logging.py
"""
Java 规则 - 检查调试日志语句
功能：检测代码中的 System.out.println, System.err.println, Log.d, Log.v
这些调试日志应该在提交代码前移除
"""
import re
from typing import List

from src.local_rules.base_rule import BaseRule, RuleFinding
from src.diff_parser import DiffChange, FileDiff


DEBUG_LOG_PATTERNS = [
    (re.compile(r'System\.out\.println'), 'System.out.println'),
    (re.compile(r'System\.err\.println'), 'System.err.println'),
    (re.compile(r'Log\.d\b'), 'Log.d'),
    (re.compile(r'Log\.v\b'), 'Log.v'),
]


class DebugLoggingRule(BaseRule):
    """检查不应提交的调试日志语句。"""

    @property
    def name(self) -> str:
        return "Java-DebugLogging"

    @property
    def description(self) -> str:
        return "检测调试日志语句（如System.out.println、Log.d），这些语句应在提交前移除"

    def check_diff(self, file_diff: FileDiff, change: DiffChange) -> List[RuleFinding]:
        findings = []
        content = change.content.strip()
        line_full = change.content

        if self._is_line_comment(content):
            return findings

        for pattern, display_str in DEBUG_LOG_PATTERNS:
            match = pattern.search(line_full)
            if match:
                if self._is_pattern_in_string(line_full, match.start(), match.end()):
                    continue

                findings.append(RuleFinding(
                    file_path=file_diff.file_path,
                    line_number=change.line_number,
                    rule_name=self.name,
                    message=f"发现调试日志语句 `{display_str}`，应在提交前移除",
                    severity="BLOCK",
                    code_snippet=content
                ))

        return findings

    def check_full_file(self, file_path: str, content: str) -> List[RuleFinding]:
        findings = []
        lines = content.splitlines()
        in_multiline_comment = False

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            current_line = line

            # 处理多行注释
            if in_multiline_comment:
                if '*/' in current_line:
                    in_multiline_comment = False
                    current_line = current_line[current_line.index('*/') + 2:]
                else:
                    continue

            if '/*' in current_line:
                if '*/' in current_line and current_line.index('/*') < current_line.index('*/'):
                    continue
                else:
                    in_multiline_comment = True
                    current_line = current_line[:current_line.index('/*')]
                    if not current_line.strip():
                        continue

            if current_line.strip().startswith('//'):
                continue

            for pattern, display_str in DEBUG_LOG_PATTERNS:
                match = pattern.search(current_line)
                if match:
                    if self._is_pattern_in_string(current_line, match.start(), match.end()):
                        continue

                    findings.append(RuleFinding(
                        file_path=file_path,
                        line_number=i,
                        rule_name=self.name,
                        message=f"发现调试日志语句 `{display_str}`，应在提交前移除",
                        severity="BLOCK",
                        code_snippet=line_stripped
                    ))

        return findings
```

重复处理其他 Java 规则，保持逻辑不变，只改文件名和加注释：
- `hardcoded_secrets.py` → `java_rule_hardcoded_secrets.py`
- `unclosed_resources.py` → `java_rule_unclosed_resources.py`
- `npe_risk.py` → `java_rule_npe_risk.py`
- `memory_leak.py` → `java_rule_memory_leak.py`

- [ ] **Step 3: 重命名 Android 规则文件并补充头部注释**

**hardcoded_urls.py → `android_rule_hardcoded_urls.py`
**viewholder_pattern.py → `android_rule_viewholder_pattern.py`
**binary_files.py → `android_rule_binary_files.py`

每个文件加头部注释说明规则功能。

- [ ] **Step 4: 删除旧目录**

```bash
rm -rf src/local_rules/java_rules src/local_rules/android_rules src/local_rules/kotlin_rules
```

- [ ] **Step 5: Commit**

```bash
git add src/local_rules/common_rules
git rm -r src/local_rules/java_rules src/local_rules/android_rules src/local_rules/kotlin_rules
git commit -m "refactor: 重构通用规则重命名，按新命名规范 java_rule_*/android_rule_*

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
"
```

---

### Task 2: 创建 pos_project_rules 目录结构

**Files:**
- Create: `src/local_rules/pos_project_rules/__init__.py`
- Create: `src/local_rules/pos_project_rules/payment/__init__.py`
- Create: 其他三个项目目录

- [ ] **Step 1: 创建顶层目录和空 __init__.py

```bash
mkdir -p src/local_rules/pos_project_rules
mkdir -p src/local_rules/pos_project_rules/payment
mkdir -p src/local_rules/pos_project_rules/cashier
mkdir -p src/local_rules/pos_project_rules/mis
mkdir -p src/local_rules/pos_project_rules/mtms
```

```python
# src/local_rules/pos_project_rules/__init__.py
"""POS 各项目特有规则 - 按项目分类存放每个项目自己的业务规则和配置
每个项目一个子目录，每个项目配置 ENABLED_RULES
"""
```

- [ ] **Step 2: 创建每个项目的 __init__.py 模板**

以 payment 为例，其他项目类似（显示名称不同：

```python
# src/local_rules/pos_project_rules/payment/__init__.py
"""收单软件项目 - 启用规则配置"""

# 从通用规则池导入需要的规则
from src.local_rules.common_rules.java_rule_debug_logging import DebugLoggingRule
from src.local_rules.common_rules.java_rule_hardcoded_secrets import HardcodedSecretsRule
from src.local_rules.common_rules.java_rule_unclosed_resources import UnclosedResourcesRule
from src.local_rules.common_rules.java_rule_npe_risk import NPERiskRule
from src.local_rules.common_rules.java_rule_memory_leak import MemoryLeakRule
from src.local_rules.common_rules.android_rule_hardcoded_urls import HardcodedUrlsRule
from src.local_rules.common_rules.android_rule_viewholder_pattern import ViewHolderPatternRule
from src.local_rules.common_rules.android_rule_binary_files import BinaryFilesRule

# GUI 下拉框显示名称
PROJECT_DISPLAY_NAME = "收单软件"

# 本项目启用的规则列表 → 只加载这里列出的规则
ENABLED_RULES = [
    DebugLoggingRule(),
    HardcodedSecretsRule(),
    UnclosedResourcesRule(),
    NPERiskRule(),
    MemoryLeakRule(),
    HardcodedUrlsRule(),
    ViewHolderPatternRule(),
    BinaryFilesRule(),
    # 如需添加收单特有规则，在这里导入并添加实例
]
```

```python
# src/local_rules/pos_project_rules/cashier/__init__.py
"""收银台软件项目 - 启用规则配置"""

# ... 和 payment 相同，PROJECT_DISPLAY_NAME = "收银台软件"
# ENABLED_RULES = [...]
```

```python
# src/local_rules/pos_project_rules/mis/__init__.py
PROJECT_DISPLAY_NAME = "MIS通道软件"
```

```python
# src/local_rules/pos_project_rules/mtms/__init__.py
PROJECT_DISPLAY_NAME = "MTMS设备管理"
```

- [ ] **Step 3: Commit

```bash
git add src/local_rules/pos_project_rules
git commit -m "feat: 新增 pos_project_rules 目录结构，四个项目初始配置

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
"
```

---

### Task 3: 修改 src/local_rules/__init__.py - 新增 load_project_rules 函数

**Files:**
- Modify: `src/local_rules/__init__.py`

- [ ] **Step 1: 修改文件，新增函数

完整新代码替换原有代码：

```python
import importlib
import pkgutil
import logging
from typing import List, Tuple, Optional

from src.local_rules.base_rule import BaseRule

logger = logging.getLogger(__name__)


def load_all_rules() -> List[BaseRule]:
    """Dynamically load all rule classes from all submodules."""
    rules: List[BaseRule] = []

    # Find all subpackages under local_rules
    import src.local_rules
    for _, package_name, is_pkg in pkgutil.iter_modules(src.local_rules.__path__):
        if not is_pkg:
            continue

        try:
            # Import the package
            pkg = importlib.import_module(f"src.local_rules.{package_name}")

            # Load all modules from this package
            for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
                try:
                    module = importlib.import_module(f"{pkg.__name__}.{module_name}")

                    # Look for all BaseRule subclasses in the module
                    for attr_name in dir(module):
                        try:
                            attr = getattr(module, attr_name)
                            if isinstance(attr, type) and issubclass(attr, BaseRule) and attr != BaseRule:
                                rules.append(attr())
                        except Exception as e:
                            logger.warning(f"Failed to process attribute {attr_name} in module {module.__name__}: {e}")
                            continue

                except Exception as e:
                    logger.warning(f"Failed to load module {package_name}.{module_name}: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Failed to load package {package_name}: {e}")
            continue

    return rules


def list_available_projects() -> List[Tuple[str, str]]:
    """List all available projects for GUI dropdown.

    Returns:
        List of (project_key, display_name) tuples.
    """
    projects: List[Tuple[str, str]] = []

    import src.local_rules.pos_project_rules as pos_package
    for _, project_key, is_pkg in pkgutil.iter_modules(pos_package.__path__):
        if not is_pkg:
            continue
        try:
            project_module = importlib.import_module(f"src.local_rules.pos_project_rules.{project_key}")
            if hasattr(project_module, "PROJECT_DISPLAY_NAME"):
                display_name = project_module.PROJECT_DISPLAY_NAME
                projects.append((project_key, display_name))
        except Exception as e:
            logger.warning(f"Failed to load project {project_key}: {e}")
            continue

    return projects


def load_project_rules(project_key: str) -> List[BaseRule]:
    """Load rules for specific project.

    Args:
        project_key: project directory name in pos_project_rules.

    Returns:
        List of enabled rules for this project as configured in the project's __init__.py.
    """
    try:
        module = importlib.import_module(f"src.local_rules.pos_project_rules.{project_key}")
        if hasattr(module, "ENABLED_RULES"):
            return module.ENABLED_RULES
        else:
            logger.warning(f"Project {project_key} has no ENABLED_RULES config, returning empty list")
            return []
    except Exception as e:
        logger.error(f"Failed to load project rules for {project_key}: {e}")
        return []
```

- [ ] **Step 2: Commit

```bash
git add src/local_rules/__init__.py
git commit -m "feat: 新增 load_project_rules 和 list_available_projects 函数，支持按项目加载规则

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
"
```

---

### Task 4: 重构 AI 提示词目录结构

**Files:**
- Rename: `java-diff-review.md` → `diff-review.md`
- Rename: `android-full-review.md` → `full-review.md`
- Delete: `kotlin-diff-review.md`
- Create: `src/ai_reviewer/prompt_templates/pos_projects/` 四个项目目录

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p src/ai_reviewer/prompt_templates/pos_projects
mkdir -p src/ai_reviewer/prompt_templates/pos_projects/payment
mkdir -p src/ai_reviewer/prompt_templates/pos_projects/cashier
mkdir -p src/ai_reviewer/prompt_templates/pos_projects/mis
mkdir -p src/ai_reviewer/prompt_templates/pos_projects/mtms
```

- [ ] **Step 2: 重命名通用提示词**

```bash
mv src/ai_reviewer/prompt_templates/java-diff-review.md src/ai_reviewer/prompt_templates/common/diff-review.md
mv src/ai_reviewer/prompt_templates/android-full-review.md src/ai_reviewer/prompt_templates/common/full-review.md
rm src/ai_reviewer/prompt_templates/kotlin-diff-review.md
```

更新内容：`diff-review.md` 内容更新为通用提示词：

```
你是一个专业的 Android Java 代码审查 AI。

你审查的是本次提交的代码 diff 增量内容，需要仔细分析代码变更，找出潜在的 bug、安全问题、不规范的写法和性能问题。

请严格按照以下要求输出结果：
1. 必须输出严格的 JSON 格式，内容是一个包含 findings 数组的 JSON 对象
2. 每个 finding 必须包含以下字段：
   - file_path: 发生问题的文件路径
   - line_start: 问题起始行号
   - line_end: 问题结束行号
   - issue_type: 问题类型，只能是以下之一：BUG/PERFORMANCE/STYLE/SECURITY
   - severity: 严重程度，只能是以下之一：BLOCK/WARNING
   - message: 问题描述
   - suggestion: 修复建议（可选）
3. 如果你没有发现任何问题，返回 {"findings": []}

输出示例：
```json
{
  "findings": [
    {
      "file_path": "path/to/file.java",
      "line_start": 10,
      "line_end": 15,
      "issue_type": "BUG",
      "severity": "BLOCK",
      "message": "这里有一个空指针异常风险的问题，当对象为null时调用其方法会抛出异常",
      "suggestion": "建议在调用方法前先进行null检查"
    }
  ]
}
```
```

`full-review.md`：

```
你是一个专业的 Android 代码审查 AI。

你审查的是整个 Android Java/Kotlin 源文件的完整内容，需要仔细分析代码，找出潜在的 bug、安全问题、不规范的写法、性能问题和不好的实践。

请严格按照以下要求输出结果：
1. 必须输出严格的 JSON 格式，内容是一个包含 findings 数组的 JSON 对象
2. 每个 finding 必须包含以下字段：
   - file_path: 发生问题的文件路径
   - line_start: 问题起始行号
   - line_end: 问题结束行号
   - issue_type: 问题类型，只能是以下之一：BUG/PERFORMANCE/STYLE/SECURITY
   - severity: 严重程度，只能是以下之一：BLOCK/WARNING
   - message: 问题描述
   - suggestion: 修复建议（可选）
3. 如果你没有发现任何问题，返回 {"findings": []}

输出示例：
```json
{
  "findings": [
    {
      "file_path": "path/to/MyActivity.java",
      "line_start": 25,
      "line_end": 30,
      "issue_type": "PERFORMANCE",
      "severity": "WARNING",
      "message": "在主线程中进行网络请求会导致应用卡顿，影响用户体验",
      "suggestion": "建议使用异步任务、线程池或协程在后台线程中执行网络请求"
    }
  ]
}
```
```

- [ ] **Step 3: 创建每个项目的 __init__.py 空配置

```python
# src/ai_reviewer/prompt_templates/pos_projects/payment/__init__.py
"""收单软件项目 - AI提示词配置

本项目启用的提示词列表（文件名带 .md 后缀）
自动识别规则：
- full 权重高于 diff → 文件名同时含 full 和 diff 按 full 处理
- 文件名包含 "diff" (大小写不敏感) → 增量审查提示词
- 文件名包含 "full" (大小写不敏感) → 全量审查提示词
- 都不包含 → 默认按全量审查处理
"""

# 如果项目不需要自定义提示词，ENABLED_PROMPTS 留空数组即可 → 自动使用通用提示词
ENABLED_PROMPTS = [
    # 示例：如果你有自定义提示词：
    # "payment-sensitive-diff.md",
    # "payment-security-full.md",
]
```

其他三个项目 `cashier`, `mis`, `mtms` 照此创建。

- [ ] **Step 4: 创建 __init__.py 入口**

```python
# src/ai_reviewer/prompt_templates/__init__.py
"""AI提示词加载模块 - 按项目加载提示词
"""
import os
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def get_project_prompts(project_key: Optional[str] = None) -> Tuple[str, str]:
    """Get the prompt template paths (without extension) for given project.

    Args:
        project_key: project key (directory name under pos_projects,
                     None for default prompts.

    Returns:
        (diff_template_name, full_template_name) -> both are file names
        name does not include .md extension or common/ or pos_projects/ prefix.
        If project has multiple matches, last one wins.
        If not found, fall back to default.
    """
    diff_name = None
    full_name = None

    if project_key:
        try:
            # 导入项目配置模块
            import importlib
            module = importlib.import_module(f"src.ai_reviewer.prompt_templates.pos_projects.{project_key}")
            if hasattr(module, "ENABLED_PROMPTS"):
                enabled_prompts = module.ENABLED_PROMPTS
                # iterate from last to first, last matching wins
                for prompt_file in reversed(enabled_prompts):
                    base_name = prompt_file.rsplit('.', 1)[0]  # remove .md
                    lower_name = prompt_file.lower()
                    if diff_name is None and 'diff' in lower_name:
                        diff_name = base_name
                    if full_name is None and 'full' in lower_name:
                        full_name = base_name
                    # full 权重更高，先找了 diff 后面又找到 full，替换 diff 覆盖
                    if 'full' in lower_name:
                        full_name = base_name
                        if 'diff' in lower_name:
                            diff_name = None  # full 覆盖 diff，权重更高
        except Exception as e:
                    logger.warning(f"Failed to load prompts for project {project_key}: {e}")

    # 兜底：没找到用默认
    if diff_name is None:
        diff_name = "common/diff-review"
    if full_name is None:
        full_name = "common/full-review"

    return diff_name, full_name


def load_prompt_content(template_name: str) -> str:
    """Load prompt template content from file by name.

    Args:
        template_name: template name like "common/diff-review" or "pos_projects/payment/xxx"

    Returns:
        Full content of the template file.
    """
    # 构建完整路径相对于 src/ai_reviewer/prompt_templates/
    full_path = os.path.join(
        os.path.dirname(__file__),
        template_name + ".md"
    )
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()
```

- [ ] **Step 5: Commit**

```bash
git add src/ai_reviewer/prompt_templates/
git commit -m "refactor: 重构AI提示词目录结构，支持按项目配置提示词

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
"
```

---

### Task 5: 修改 GUI launcher 新增项目下拉框

**Files:**
- Modify: `src/gui_launcher.py`

- [ ] **Step 1: 修改 create_widgets，新增下拉框

在 `self.project_dir` 之后加：

```python
# 选中的项目目录
self.project_dir = tkinter.StringVar()
# 选中的项目类型
self.project_key = tkinter.StringVar()

self.create_widgets()
```

在 create_widgets 方法中，在"项目目录"之前加入：

```python
# 项目类型选择
frame0 = ttk.Frame(self.root)
frame0.pack(fill='x', padx=20, pady=5)

ttk.Label(frame0, text="项目类型:").pack(anchor='w')

from src.local_rules import list_available_projects
projects = list_available_projects()
project_keys = [p[0] for p in projects]
project_display = [p[1] for p in projects]

# 默认选中第一个（收单软件）
if project_display:
    self.project_key.set(project_display[0])
    self.default_project_key = project_keys[0]

combo = ttk.Combobox(frame0, textvariable=self.project_key, values=project_display, state='readonly')
combo.pack(fill='x', pady=5)

# 存储 key 把显示名映射回去找 key
self.project_key_to_key = dict(zip(project_display, project_keys))

# 项目目录选择
frame1 = ttk.Frame(self.root)
... rest unchanged
```

然后在 `start_review` 中，获取选中项目key：

```python
display_name = self.project_key.get()
project_key = self.project_key_to_key[display_name]
...
# 传递 project_key 给 main，通过环境变量或命令行参数
...
```

完整修改 `start_review` 最后调用 main：

```python
# 运行主程序，传递项目参数
try:
    # 切换工作目录
    os.chdir(directory)

    # 导入并运行main
    from src.main import main
    sys.argv = [sys.argv[0], '--project', project_key]
    result = main()
```

- [ ] **Step 2: Commit

```bash
git add src/gui_launcher.py
git commit -m "feat: GUI新增项目类型下拉选择框，默认选中收单软件

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
"
```

---

### Task 6: 修改 main.py 支持 --project 参数

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: 增加命令行参数解析，在 run_full_file_review 中按项目加载提示词

修改导入新增：

```python
import argparse
...
from src.ai_reviewer.prompt_templates import get_project_prompts, load_prompt_content
...

def main():
    """主审查流程"""
    try:
        # 解析命令行参数
        parser = argparse.ArgumentParser()
        parser.add_argument('--project', help='Project key to load rules and prompts for')
        args = parser.parse_args()
        project_key = args.project
        ...
        # 步骤4: 在diff上运行本地规则
        logger.info("步骤4: 在差异上运行本地规则")
        if project_key:
            from src.local_rules import load_project_rules
            rules = load_project_rules(project_key)
        else:
            rules = load_all_rules()
        ...
```

在 run_full_file_review 修改：

```python
# 如果已配置，运行AI审查
if ai_client:
    try:
        logger.info(f"[{idx}/{len(file_diffs)}] 正在AI审查: {file_diff.file_path}")
        # 根据项目获取提示词
        if 'project_key' in locals():
            diff_template_name, full_template_name = get_project_prompts(project_key)
        else:
            diff_template_name, full_template_name = get_project_prompts(None)
        prompt_content = load_prompt_content(full_template_name)
        ai_result = ai_client.review_full_file(file_diff.file_path, file_content, prompt_content)
        ...
```

diff 同理。

- [ ] **Step 2: Commit**

```bash
git add src/main.py
git commit -m "feat: main.py新增--project命令行参数，支持按项目加载规则和提示词

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
"
```

---

### Task 7: 优化 README.md 整体重构，对 Java 开发者友好

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新扩展开发指南部分**

更新目录结构说明，新增：

```
## 目录结构说明

```
src/local_rules/
├── base_rule.py              # 所有规则抽象基类，不用改
├── common_rules/            # 通用规则池，各项目共享
│   ├── java_rule_*.py       # Java 语言规则，前缀 java_rule_ 一眼识别
│   └── android_rule_*.py    # Android 框架规则，前缀 android_rule_
└── pos_project_rules/       # 按项目分类，每个项目一个目录
    ├── payment/             # 收单项目
    │   ├── __init__.py      # ← 在这里配置本项目要启用哪些规则
    │   └── payment_*.py     # 收单项目自有规则，前缀 payment_
    ├── cashier/             # 收银台项目
    ├── mis/                # MIS项目
    └── mtms/               # MTMS项目
```

**AI 提示词目录结构完全对齐：

```
src/ai_reviewer/prompt_templates/
├── common/                 # 通用提示词
│   ├── diff-review.md      # 默认增量审查提示词
│   └── full-review.md      # 默认全量审查提示词
└── pos_projects/           # 按项目分类，目录名和 local 对齐
    ├── payment/
    │   ├── __init__.py      # ← 在这里配置本项目要启用哪些提示词
    │   └── *.md             # 每个提示词单独一个文件
    ...
```

然后新增给 Java 开发者的扩展指南：**如何新增一条规则** 一步步来。

- [ ] **Step 2: Commit

```bash
git add README.md
git commit -m "docs: README整体优化，对Java开发者更友好，补充架构说明

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
"
```

---

### Task 8: 验证测试

- [ ] **Step 1: 运行 GUI 测试启动

```bash
python src/gui_launcher.py
```

验证 GUI 能启动，下拉框显示四个项目，默认选中第一个。

- [ ] **Step 2: 运行 pytest 测试现有单元测试（如果有）

```bash
python -m pytest tests/ -v
```

确认所有测试通过。

