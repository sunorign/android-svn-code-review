# 本地规则编写指南

## 什么是本地规则？

本地规则是用于自定义代码审查逻辑的扩展机制，允许你通过继承基础规则类并实现特定方法来创建自定义代码检查规则。通过本地规则，你可以针对项目特定的代码规范、最佳实践或业务逻辑进行定制化审查。

## 基本步骤

### 1. 继承 BaseRule 基类

所有本地规则都需要继承项目提供的 `BaseRule` 基类。该基类提供了基础的规则框架和通用工具方法。

### 2. 实现核心检查方法

你需要实现两个核心检查方法：

#### `check_diff(self, diff_content: str, file_path: str) -> list`

该方法用于增量检查，只审查代码变更部分。

- `diff_content`: Git diff 格式的变更内容
- `file_path`: 当前审查的文件路径
- 返回值: 包含所有发现问题的列表

#### `check_full_file(self, file_content: str, file_path: str) -> list`

该方法用于全量文件检查，会审查整个文件内容。

- `file_content`: 完整的文件内容
- `file_path`: 当前审查的文件路径
- 返回值: 包含所有发现问题的列表

### 3. 设置规则严重性

通过类属性 `severity` 来设置规则的严重性级别，支持两种选项：
- `BLOCK`: 严重问题，会阻止代码合并
- `WARNING`: 警告问题，仅提示但不阻止合并

## 完整示例代码

```python
from typing import List, Dict
from ..base_rule import BaseRule

class ExampleLocalRule(BaseRule):
    # 设置规则名称和描述
    name = "example-local-rule"
    description = "示例本地规则，用于演示如何编写自定义规则"

    # 设置严重性为 WARNING
    severity = "WARNING"

    def check_diff(self, diff_content: str, file_path: str) -> List[Dict]:
        """增量检查示例"""
        issues = []

        # 解析diff内容，检查变更行
        lines = diff_content.split("\n")
        for line_num, line in enumerate(lines):
            # 示例：检查是否包含 TODO 注释
            if "TODO" in line and line.startswith("+"):
                issues.append({
                    "file_path": file_path,
                    "line_start": line_num,
                    "line_end": line_num,
                    "issue_type": "todo-comment",
                    "severity": self.severity,
                    "message": "发现未完成的TODO注释",
                    "suggestion": "请完成TODO事项或移除注释"
                })

        return issues

    def check_full_file(self, file_content: str, file_path: str) -> List[Dict]:
        """全量检查示例"""
        issues = []

        # 检查整个文件内容
        lines = file_content.split("\n")
        for line_num, line in enumerate(lines):
            # 示例：检查是否有过长的行
            if len(line) > 120:
                issues.append({
                    "file_path": file_path,
                    "line_start": line_num + 1,
                    "line_end": line_num + 1,
                    "issue_type": "line-too-long",
                    "severity": "WARNING",
                    "message": f"行长度超过120字符（当前{len(line)}字符）",
                    "suggestion": "请拆分过长的代码行"
                })

        return issues
```

## 加载自定义规则

编写完成的本地规则文件需要放置在项目指定的规则目录中，系统会自动扫描加载该目录下的所有规则类。

### 规则存放目录

将你的规则文件放在 `rules/local/` 目录下，例如：
```
rules/local/example_rule.py
```

系统会自动扫描该目录下所有 `.py` 文件，并加载其中继承自 `BaseRule` 的规则类。

## 常见规则示例参考

### 示例1：检查print语句使用

```python
from ..base_rule import BaseRule

class NoPrintStatementRule(BaseRule):
    name = "no-print-statement"
    description = "禁止在代码中使用print语句"
    severity = "WARNING"

    def check_full_file(self, file_content: str, file_path: str) -> list:
        issues = []
        import ast

        try:
            tree = ast.parse(file_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
                    line_num = node.lineno
                    issues.append({
                        "file_path": file_path,
                        "line_start": line_num,
                        "line_end": line_num,
                        "issue_type": "forbidden-print",
                        "severity": self.severity,
                        "message": "代码中禁止使用print语句",
                        "suggestion": "请使用logging模块代替print"
                    })
        except:
            pass

        return issues
```

### 示例2：检查函数长度

```python
from ..base_rule import BaseRule

class FunctionLengthRule(BaseRule):
    name = "function-length-limit"
    description = "检查函数长度是否超过限制"
    severity = "WARNING"
    max_lines = 50

    def check_full_file(self, file_content: str, file_path: str) -> list:
        issues = []
        import ast

        try:
            tree = ast.parse(file_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    start_line = node.lineno
                    end_line = node.end_lineno
                    func_length = end_line - start_line + 1

                    if func_length > self.max_lines:
                        issues.append({
                            "file_path": file_path,
                            "line_start": start_line,
                            "line_end": end_line,
                            "issue_type": "function-too-long",
                            "severity": self.severity,
                            "message": f"函数'{node.name}'长度({func_length}行)超过限制({self.max_lines}行)",
                            "suggestion": "请拆分函数为多个较小的函数"
                        })
        except:
            pass

        return issues
```

## 最佳实践

1. **保持规则简洁**：每个规则只专注于检查一种特定的问题
2. **提供清晰的提示**：错误信息和建议要明确，帮助开发者快速理解问题并修复
3. **合理设置严重性**：对于严重影响代码质量或功能的问题使用 BLOCK，对于风格或优化建议使用 WARNING
4. **充分测试**：在提交规则前，使用不同的代码场景测试你的规则
5. **遵循现有规范**：参考已有的内置规则实现，保持代码风格一致