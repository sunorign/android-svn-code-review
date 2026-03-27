# AI 提示词编写规范

## AI 审查提示词的作用

AI 审查提示词是用于指导代码审查 AI 模型进行代码分析的指令集合。通过精心设计的提示词，可以让 AI 模型按照特定的标准和要求来审查代码变更，识别潜在问题、安全漏洞、代码质量问题等。

提示词需要包含明确的规则说明、检查标准和输出格式要求，确保 AI 模型能够理解期望的代码审查规范。

## 基本要求

### 1. 强制 JSON 输出格式

AI 审查提示词必须要求模型输出严格符合规范的 JSON 格式，以便后续的处理和展示。

### 2. 输出字段含义

每个问题报告必须包含以下字段：

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `file_path` | 字符串 | 问题所在的文件路径 |
| `line_start` | 整数 | 问题起始行号 |
| `line_end` | 整数 | 问题结束行号 |
| `issue_type` | 字符串 | 问题类型（如 "security"、"style"、"performance" 等） |
| `severity` | 字符串 | 严重程度，必须为 "BLOCK" 或 "WARNING" |
| `message` | 字符串 | 问题描述 |
| `suggestion` | 字符串 | 修复建议 |

### 3. 字段取值规范

- `issue_type`: 使用简洁的英文关键词，如 `security`, `style`, `performance`, `best_practice` 等
- `severity`: 仅允许值 `BLOCK`（阻塞）或 `WARNING`（警告）
- 所有字符串字段应使用 UTF-8 编码
- 避免使用特殊字符，建议使用标准 ASCII 字符

## 示例提示词结构

### 通用代码质量检查提示词

```
你现在是一个专业的代码审查专家。请严格按照以下规范检查用户提供的代码变更。

## 检查规范

1. 检查代码是否符合PEP8规范
2. 检查是否有未使用的变量
3. 检查函数长度是否合理
4. 检查是否有重复代码
5. 检查是否有潜在的安全问题

## 输出要求

必须输出JSON格式，包含以下字段：
- file_path: 文件路径
- line_start: 问题起始行号
- line_end: 问题结束行号
- issue_type: 问题类型（security/style/performance/best_practice等）
- severity: 严重程度（BLOCK/WARNING）
- message: 问题描述
- suggestion: 修复建议

## 输入示例

文件: test.py
代码变更:
def calculate_price(quantity, price):
    if quantity > 100:
        discount = 0.9
    else:
        discount = 1.0

    # 计算总价
    total = quantity * price * discount
    print(f"Total price: {total}")

    return total

## 输出示例

[
  {
    "file_path": "test.py",
    "line_start": 9,
    "line_end": 9,
    "issue_type": "style",
    "severity": "WARNING",
    "message": "使用了print语句而非logging模块",
    "suggestion": "请使用logging模块替代print语句"
  }
]
```

### 安全问题检查提示词

```
你现在是一个专业的代码安全审查专家。请严格按照以下规范检查用户提供的代码变更。

## 检查规范

1. 检查SQL注入风险
2. 检查XSS攻击漏洞
3. 检查硬编码密码
4. 检查未加密的敏感数据
5. 检查权限控制问题

## 输出要求

必须输出JSON格式，包含以下字段：
- file_path: 文件路径
- line_start: 问题起始行号
- line_end: 问题结束行号
- issue_type: 问题类型（security/style/performance/best_practice等）
- severity: 严重程度（BLOCK/WARNING）
- message: 问题描述
- suggestion: 修复建议

## 输入示例

文件: auth.py
代码变更:
def login(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    return cursor.fetchone()

## 输出示例

[
  {
    "file_path": "auth.py",
    "line_start": 2,
    "line_end": 2,
    "issue_type": "security",
    "severity": "BLOCK",
    "message": "存在SQL注入风险",
    "suggestion": "请使用参数化查询防止SQL注入"
  }
]
```

## 添加新提示词模板

### 模板存放目录

AI 提示词模板需要放置在项目的 `prompts/` 目录下，例如：

```
prompts/
├── python/
│   ├── code_quality.prompt
│   └── security.prompt
├── javascript/
│   ├── eslint.prompt
│   └── security.prompt
└── java/
    └── code_style.prompt
```

### 目录结构规范

- 按照语言或技术栈创建子目录（如 `python/`, `javascript/`）
- 提示词文件使用 `.prompt` 或 `.txt` 扩展名
- 文件名应该清晰描述其功能（如 `code_quality.prompt`）

### 系统加载机制

系统会在运行审查前：
1. 扫描 `prompts/` 目录及其子目录
2. 根据当前审查文件的语言类型匹配对应的提示词
3. 自动加载并应用匹配的提示词

## 最佳实践

### 1. 明确检查范围

提示词中应明确指出需要检查的具体规范，避免模糊不清的描述。

**好的示例：**
```
检查代码是否符合PEP8规范
- 缩进使用4个空格
- 每行不超过120个字符
- 禁止使用单行if语句
```

### 2. 提供示例

在提示词中提供输入和输出的示例，帮助AI模型更好地理解预期。

### 3. 使用专业术语

使用标准的代码审查术语，如：
- "未使用的变量"
- "潜在的SQL注入风险"
- "硬编码密码"

### 4. 保持简洁

提示词应简洁明了，避免冗余信息。

### 5. 定期更新

根据项目需求和代码规范的演变，定期更新提示词。

## 测试和验证

在使用新提示词前，建议进行以下验证：
1. 使用示例代码测试提示词
2. 检查输出格式是否正确
3. 评估问题报告的准确性
4. 调整和优化提示词内容

通过以上规范和最佳实践，你可以创建高质量的AI审查提示词，提高代码审查的效率和准确性。