# 配置 JSON 化与 GUI 入口重构 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 AI 客户端配置从环境变量改为 JSON 文件配置，添加 GUI 双击启动入口，更新 README.md 突出客户端使用方式，实现开箱即用。

**Architecture:** 保持原有模块化架构不变。新增 JSON 配置加载器替换环境变量读取，新增 tkinter GUI 启动器提供文件夹选择和自动打开报告功能。README 文档结构调整，将服务端钩子配置移至附录。

**Tech Stack:** Python 3.8+, json 标准库, tkinter 标准库, webbrowser 标准库，无额外第三方依赖。

---

### Task 1: 创建 JSON 配置文件

**Files:**
- Create: `src/ai_reviewer/ai_client_config.json`

- [ ] **Step 1: Write the JSON configuration file**

```json
{
  "default_provider": "openrouter",
  "api_timeout": 60,
  "providers": {
    "claude": {
      "api_key": "",
      "api_url": "https://api.anthropic.com/v1",
      "model": "claude-3-opus-20240229",
      "max_tokens": 4096
    },
    "openrouter": {
      "api_key": "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",
      "api_url": "https://openrouter.ai/api/v1/chat/completions",
      "model": "minimax/minimax-m2.5",
      "max_tokens": 4096,
      "http_referer": ""
    },
    "ollama": {
      "api_base": "http://localhost:11434",
      "model": "llama2",
      "max_tokens": 4096
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/ai_reviewer/ai_client_config.json
git commit -m "feat: add JSON configuration file for AI clients"
```

---

### Task 2: 重构 config.py 支持 JSON 加载

**Files:**
- Modify: `src/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Update imports and add JSON loading logic**

Replace the entire content of `src/config.py` with:

```python
import os
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Config:
    """AI客户端配置。"""
    # Anthropic Claude
    anthropic_api_key: Optional[str] = None
    anthropic_api_url: Optional[str] = None
    anthropic_model: Optional[str] = None
    anthropic_max_tokens: int = 4096

    # OpenRouter
    openrouter_api_key: Optional[str] = None
    openrouter_api_url: Optional[str] = None
    openrouter_model: Optional[str] = None
    openrouter_max_tokens: int = 4096
    openrouter_http_referer: Optional[str] = None

    # Local Ollama
    ollama_api_base: Optional[str] = None
    ollama_model: Optional[str] = None
    ollama_max_tokens: int = 4096

    # Common
    api_timeout: int = 60
    ai_provider: Optional[str] = None

    def has_ai_enabled(self) -> bool:
        """检查是否启用了AI审查。"""
        if not self.ai_provider:
            return False
        match self.ai_provider:
            case 'claude':
                return self.anthropic_api_key is not None and len(self.anthropic_api_key) > 0
            case 'openrouter':
                return self.openrouter_api_key is not None and len(self.openrouter_api_key) > 0
            case 'ollama':
                return self.ollama_api_base is not None
            case _:
                return False

    def get_active_provider(self) -> Optional[str]:
        """获取当前配置的AI提供者。"""
        return self.ai_provider


class JsonConfigLoader:
    """从JSON文件加载AI客户端配置。"""

    DEFAULT_CONFIG_PATH = os.path.join(
        os.path.dirname(__file__),
        'ai_reviewer',
        'ai_client_config.json'
    )

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> Config:
        """
        从JSON文件加载配置。

        Args:
            config_path: 可选的自定义配置路径，不指定则使用默认路径。

        Returns:
            Config 对象

        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置格式错误
        """
        if config_path is None:
            config_path = cls.DEFAULT_CONFIG_PATH

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        config = Config()

        # 加载通用配置
        config.ai_provider = data.get('default_provider')
        config.api_timeout = data.get('api_timeout', 60)

        # 加载各提供者配置
        providers = data.get('providers', {})

        # Claude
        claude_config = providers.get('claude', {})
        config.anthropic_api_key = claude_config.get('api_key')
        config.anthropic_api_url = claude_config.get('api_url')
        config.anthropic_model = claude_config.get('model')
        config.anthropic_max_tokens = claude_config.get('max_tokens', 4096)

        # OpenRouter
        openrouter_config = providers.get('openrouter', {})
        config.openrouter_api_key = openrouter_config.get('api_key')
        config.openrouter_api_url = openrouter_config.get('api_url')
        config.openrouter_model = openrouter_config.get('model')
        config.openrouter_max_tokens = openrouter_config.get('max_tokens', 4096)
        config.openrouter_http_referer = openrouter_config.get('http_referer', '')

        # Ollama
        ollama_config = providers.get('ollama', {})
        config.ollama_api_base = ollama_config.get('api_base')
        config.ollama_model = ollama_config.get('model')
        config.ollama_max_tokens = ollama_config.get('max_tokens', 4096)

        # 验证必要配置
        if config.ai_provider not in ['claude', 'openrouter', 'ollama', None]:
            raise ValueError(f"未知的AI提供者: {config.ai_provider}")

        return config

    @classmethod
    def load_with_fallback(cls, config_path: Optional[str] = None) -> Config:
        """
        加载配置，尝试JSON，如果失败则回退到环境变量（兼容旧方式）。

        Args:
            config_path: 可选的自定义配置路径

        Returns:
            Config 对象
        """
        try:
            return cls.load(config_path)
        except (FileNotFoundError, json.JSONDecodeError):
            # 回退到环境变量读取（兼容旧版）
            return cls._load_from_env()

    @staticmethod
    def _load_from_env() -> Config:
        """从环境变量加载配置（向后兼容）。"""
        # 保留原环境变量读取逻辑用于向后兼容
        import os
        from urllib.parse import urlparse

        ollama_api_base = os.environ.get('OLLAMA_API_BASE', 'http://localhost:11434')
        try:
            parsed = urlparse(ollama_api_base)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"OLLAMA_API_BASE的URL格式无效: {ollama_api_base}")
        except Exception as e:
            raise ValueError(f"OLLAMA_API_BASE的URL格式无效: {ollama_api_base}") from e

        default_openrouter_key = "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"

        return Config(
            anthropic_api_key=os.environ.get('ANTHROPIC_API_KEY'),
            anthropic_api_url=os.environ.get('ANTHROPIC_API_URL'),
            anthropic_model=os.environ.get('ANTHROPIC_MODEL'),
            anthropic_max_tokens=int(os.environ.get('ANTHROPIC_MAX_TOKENS', 4096)),
            openrouter_api_key=os.environ.get('OPENROUTER_API_KEY', default_openrouter_key),
            openrouter_api_url=os.environ.get('OPENROUTER_API_URL'),
            openrouter_model=os.environ.get('OPENROUTER_MODEL'),
            openrouter_max_tokens=int(os.environ.get('OPENROUTER_MAX_TOKENS', 4096)),
            ollama_api_base=ollama_api_base,
            ollama_model=os.environ.get('OLLAMA_MODEL'),
            ollama_max_tokens=int(os.environ.get('OLLAMA_MAX_TOKENS', 4096)),
            api_timeout=int(os.environ.get('API_TIMEOUT', 60)),
            ai_provider=os.environ.get('AI_REVIEW_PROVIDER', 'openrouter'),
        )
```

- [ ] **Step 2: Update existing tests if needed**

Check the existing test and update to expect new default values:

```python
# In tests/test_config.py, if testing from_env:
# default ai_provider should now be 'openrouter' by default
```

- [ ] **Step 3: Run existing tests**

```bash
python -m pytest tests/test_config.py -v
```

Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "refactor: migrate config to JSON file loading"
```

---

### Task 3: Update openrouter_client.py to use Config correctly

**Files:**
- Modify: `src/ai_reviewer/openrouter_client.py`

- [ ] **Step 1: Restore the openrouter_client to read from Config instead of hardcoding**

Replace lines 16-26 in `src/ai_reviewer/openrouter_client.py` with:

```python
    def __init__(self, config: Config):
        """
        初始化OpenRouter客户端。

        参数:
            config: 包含OpenRouter API密钥的配置对象
        """
        self.config = config
        self.api_key = config.openrouter_api_key
        self.base_url = config.openrouter_api_url or "https://openrouter.ai/api/v1/chat/completions"
        self.default_model = config.openrouter_model or "anthropic/claude-3-sonnet"
        self.max_tokens = config.openrouter_max_tokens or 4096
        self.timeout = config.api_timeout or 60
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": config.openrouter_http_referer or "",
            "Content-Type": "application/json"
        }
```

- [ ] **Step 2: Run a quick test to ensure import works**

```bash
python -c "from src.ai_reviewer.openrouter_client import OpenRouterClient; from src.config import JsonConfigLoader; cfg = JsonConfigLoader.load(); print('OK')"
```

Expected: Prints `OK` with no errors

- [ ] **Step 3: Commit**

```bash
git add src/ai_reviewer/openrouter_client.py
git commit -m "fix: restore Config-based configuration for openrouter"
```

---

### Task 4: Update ai_reviewer/__init__.py to use JsonConfigLoader

**Files:**
- Modify: `src/ai_reviewer/__init__.py`

- [ ] **Step 1: Update get_ai_client to load from JSON config**

```python
import logging
from typing import Optional

from src.config import Config, JsonConfigLoader
from src.ai_reviewer.base_client import BaseAIClient
from src.ai_reviewer.claude_client import ClaudeClient
from src.ai_reviewer.openrouter_client import OpenRouterClient
from src.ai_reviewer.local_ollama_client import LocalOllamaClient

logger = logging.getLogger(__name__)


def get_ai_client(config: Optional[Config] = None) -> Optional[BaseAIClient]:
    """Factory method to get the configured AI client."""
    if config is None:
        config = JsonConfigLoader.load()

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
        case _:
            logger.warning(f"Unknown AI provider: {provider}")
            return None
```

- [ ] **Step 2: Test the import**

```bash
python -c "from src.ai_reviewer import get_ai_client; client = get_ai_client(); print(f'Got client: {type(client).__name__}')"
```

Expected: Prints `Got client: OpenRouterClient` with no errors

- [ ] **Step 3: Commit**

```bash
git add src/ai_reviewer/__init__.py
git commit -m "refactor: update get_ai_client to use JsonConfigLoader"
```

---

### Task 5: Update main.py to use JsonConfigLoader

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: Update config loading in main**

Find where config is loaded, replace:

```python
# Before:
config = Config.load_from_env()

# After:
from src.config import JsonConfigLoader
config = JsonConfigLoader.load()
```

Check current line in `src/main.py` and update accordingly.

- [ ] **Step 2: Test main module import**

```bash
python -c "import src.main; print('Import OK')"
```

Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add src/main.py
git commit -m "refactor: update main to use JsonConfigLoader"
```

---

### Task 6: Create GUI Launcher

**Files:**
- Create: `src/gui_launcher.py`

- [ ] **Step 1: Write the GUI launcher code**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUI 启动器 - 图形化界面选择项目并启动代码审查。"""

import os
import sys
import tkinter
from tkinter import filedialog, messagebox, ttk
import webbrowser
import subprocess
import logging
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class CodeReviewGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperPower Code Review")
        self.root.geometry("500x280")
        self.root.resizable(False, False)

        # 选中的项目目录
        self.project_dir = tkinter.StringVar()

        # 是否进行全文AI审查
        self.enable_ai = tkinter.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_label = ttk.Label(
            self.root,
            text="SuperPower Code Review",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(15, 5))

        subtitle = ttk.Label(
            self.root,
            text="Android SVN 自动化代码审查工具"
        )
        subtitle.pack(pady=(0, 20))

        # 项目目录选择
        frame1 = ttk.Frame(self.root)
        frame1.pack(fill='x', padx=20, pady=5)

        ttk.Label(frame1, text="项目目录:").pack(anchor='w')

        dir_frame = ttk.Frame(frame1)
        dir_frame.pack(fill='x', pady=5)

        entry = ttk.Entry(dir_frame, textvariable=self.project_dir)
        entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

        browse_btn = ttk.Button(dir_frame, text="浏览...", command=self.browse_dir)
        browse_btn.pack(side='right')

        # AI审查选项
        ai_frame = ttk.Frame(frame1)
        ai_frame.pack(fill='x', pady=10)

        ai_check = ttk.Checkbutton(
            ai_frame,
            text="启用全文AI审查（需要配置API密钥）",
            variable=self.enable_ai
        )
        ai_check.pack(anchor='w')

        # 开始按钮
        start_btn = ttk.Button(
            self.root,
            text="开始代码审查",
            command=self.start_review,
            style='Accent.TButton'
        )
        start_btn.pack(pady=20, fill='x', padx=20)

        # 状态栏
        self.status = ttk.Label(self.root, text="就绪，请选择项目目录", foreground='gray')
        self.status.pack(pady=(0, 10))

    def browse_dir(self):
        directory = filedialog.askdirectory(
            title="选择 Android 项目根目录",
            mustexist=True
        )
        if directory:
            self.project_dir.set(directory)
            self.status.config(text=f"已选择: {os.path.basename(directory)}")

    def check_svn(self, directory: str) -> bool:
        """检查是否是 SVN 工作副本。"""
        return os.path.exists(os.path.join(directory, '.svn'))

    def start_review(self):
        directory = self.project_dir.get().strip()
        if not directory or not os.path.isdir(directory):
            messagebox.showerror("错误", "请选择有效的项目目录")
            return

        if not self.check_svn(directory):
            result = messagebox.askyesno(
                "警告",
                "该目录不是 SVN 工作副本，无法获取变更列表。\n是否继续尝试审查目录中所有 Java 文件？\n（此功能尚未实现）"
            )
            if not result:
                return

        self.status.config(text="正在运行代码审查...")
        self.root.update()

        # 运行主程序
        try:
            # 切换工作目录
            os.chdir(directory)

            # 导入并运行main
            from src.main import main
            main()

            # 查找最新生成的HTML报告
            report_dir = os.path.join(directory, 'code-review-output')
            if os.path.exists(report_dir):
                html_files = [
                    f for f in os.listdir(report_dir)
                    if f.endswith('.html') and f.startswith('review-result')
                ]
                if html_files:
                    # 按修改时间排序，最新的在最后
                    html_files.sort(
                        key=lambda f: os.path.getmtime(os.path.join(report_dir, f))
                    )
                    latest_html = os.path.join(report_dir, html_files[-1])
                    # 用浏览器打开
                    webbrowser.open(f'file://{latest_html}')
                    messagebox.showinfo(
                        "完成",
                        f"代码审查完成!\n报告已在浏览器打开:\n{latest_html}"
                    )
                else:
                    messagebox.showinfo(
                        "完成",
                        "代码审查完成，未发现问题，未生成报告。"
                    )
            else:
                messagebox.showinfo("完成", "代码审查完成！")

            self.status.config(text="完成")

        except Exception as e:
            error_msg = f"代码审查过程中出错:\n{str(e)}"
            logging.error(error_msg, exc_info=True)
            messagebox.showerror("错误", error_msg)
            self.status.config(text="出错了", foreground='red')


def main():
    # 检查tkinter是否可用
    try:
        import tkinter
    except ImportError:
        print("错误: 当前 Python 安装不包含 tkinter，请重新安装 Python 并确保勾选 tcl/tk 选项")
        sys.exit(1)

    root = tkinter.Tk()
    app = CodeReviewGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Test import**

```bash
python -c "import src.gui_launcher; print('Import OK')"
```

Expected: Prints `Import OK` (may show nothing if tkinter not available, but CI doesn't need GUI)

- [ ] **Step 3: Commit**

```bash
git add src/gui_launcher.py
git commit -m "feat: add GUI launcher with tkinter"
```

---

### Task 7: 创建 start-gui.bat 启动脚本

**Files:**
- Create: `start-gui.bat` (at project root)

- [ ] **Step 1: Write the batch file**

```batch
@echo off
chcp 65001 > nul
echo 正在启动 SuperPower Code Review...
python src/gui_launcher.py
if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请检查 Python 是否正确安装
    pause
    exit /b 1
)
```

- [ ] **Step 2: Commit**

```bash
git add start-gui.bat
git commit -m "feat: add start-gui.bat double-click launcher"
```

---

### Task 8: 重写 README.md 调整结构

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rewrite README.md with new structure**

Keep all existing content but restructure:

**New Outline:**
1. 项目介绍（强调客户端定位）
2. 核心特点
3. 功能特性
   - 本地静态规则检查（保留原样）
   - AI 辅助审查（保留原样）
4. 环境要求
5. 安装步骤（客户端优先）
6. **客户端使用方法**（新增，重点说明 GUI 方式）
7. 审查规则说明（保留原样）
8. 报告格式说明（保留原样）
9. 扩展开发指南（保留原样）
10. **附录：SVN pre-commit 服务端钩子配置**（原来的主要内容移到这里）
11. 常见问题（保留原样）

[Full content in the existing file will be rearranged according to this outline]

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: restructure README to highlight client usage, move server hooks to appendix"
```

---

### Task 9: 运行所有测试确认一切正常

**Files:**
- All tests

- [ ] **Step 1: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 2: Commit any fixes if needed**

- [ ] **Step 3: Plan complete**

