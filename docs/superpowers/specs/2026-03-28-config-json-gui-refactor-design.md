# 配置重构与 GUI 入口设计

## 项目背景

SuperPower Code Review 是一款专为 Android 开发团队设计的自动化代码审查工具。原版本使用环境变量配置 AI 客户端，主要以 SVN pre-commit 钩子方式运行。本次重构目标：

1. 将 AI 客户端配置改为 JSON 文件，便于编辑和开箱即用
2. 添加 GUI 入口脚本，让客户端用户可以更便捷使用
3. 更新 README.md，突出客户端使用说明，将服务端钩子配置移至末尾

## 设计决策

### 1. JSON 配置设计

#### 文件位置
`src/ai_reviewer/ai_client_config.json`

#### JSON 结构
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

#### 代码改动
- 新增 `JsonConfigLoader` 类负责加载和验证 JSON 配置
- 保留 `Config` 数据类结构以便下游使用，但构造方式改为从 JSON 加载
- 移除从环境变量读取的逻辑（或降级为备选方案）
- 预填充现有的 openrouter 测试配置，实现开箱即用

### 2. GUI 入口设计

#### 文件结构
```
project-root/
├── start-gui.bat          # 双击启动脚本
└── src/
    └── gui_launcher.py   # GUI 启动器逻辑
```

#### `start-gui.bat` 内容
```batch
@echo off
chcp 65001 > nul
python src/gui_launcher.py
pause
```

#### `gui_launcher.py` 流程
1. 检查 tkinter 是否可用（Python 自带，通常无需额外安装）
2. 弹出文件夹选择对话框，让用户选择要审查的 Android 项目根目录
3. 切换工作目录到所选文件夹
4. 调用 `svn diff` 获取变更（复用现有逻辑）
5. 运行静态规则检查 + AI 审查（复用现有流程）
6. 审查完成后，自动用默认浏览器打开 HTML 报告

#### 用户使用流程（开箱即用）
1. 下载/克隆项目到本地
2. 如果需要换模型，编辑 `src/ai_reviewer/ai_client_config.json`
3. 双击 `start-gui.bat`
4. 选择 Android 项目文件夹
5. 等待审查完成，自动查看报告

### 3. README.md 重构

#### 新结构
1. **项目介绍** - 明确定位为**客户端开发人员**使用的代码审查工具
2. **核心特点** - 保留原内容，强调开箱即用
3. **功能特性** - 保留原内容
4. **环境要求** - 保留原内容
5. **安装步骤** - 突出客户端安装
   - 第一步：克隆/下载项目
   - 第二步：检查配置文件（已预配置，可直接使用）
   - 第三步：双击 start-gui.bat 启动
6. **使用方法** - 详细说明 GUI 使用流程
7. **审查规则说明** - 保留原内容
8. **报告格式说明** - 保留原内容
9. **扩展开发指南** - 保留原内容
10. **附录：SVN pre-commit 服务端钩子配置** - 将原来的主要内容移到这里，放在文档最后

## 实现清单

1. 创建 `src/ai_reviewer/ai_client_config.json` 配置文件
2. 修改 `src/config.py`，改用 JSON 配置加载
3. 创建 `src/gui_launcher.py`
4. 创建 `start-gui.bat` 在项目根目录
5. 重写 `README.md`，调整结构和内容

## 依赖影响

- 不引入新的第三方依赖，tkinter 是 Python 标准库
- 保持向后兼容：原有的命令行调用方式和 SVN 钩子方式仍然可用
- 现有 AI 客户端代码无需大规模改动，只需要改变配置读取方式
