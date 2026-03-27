---
name: 统一报告格式设计
description: 代码审查工具统一报告格式设计文档，包含五列固定格式
type: project
---

# 统一报告格式设计文档

## 概述

重新设计代码审查工具的输出格式，采用五列固定格式，使用AI进行问题类型分类和修复建议生成。

## 设计目标

**完全放弃现有格式，采用全新五列结构：**

1. **优先级**：严重/一般/轻微（严重不通过需立即修复，一般-建议修复，轻微-可以后续修复）
2. **问题类型**：由AI分析问题类型（内存泄露、超时处理不足等）
3. **位置**：问题所在位置（文件路径:行号）
4. **说明**：问题的详细说明
5. **修复建议**：AI生成的修复建议

## 架构设计

### 数据流程

```
原始发现（RuleFinding/AIReviewFinding）
    ↓
AI 处理模块（新增）
    ↓
统一格式（UnifiedFinding）
    ↓
报告生成（文本/HTML/JSON，表格格式）
```

### 核心组件

#### 1. UnifiedFinding 类

```python
@dataclass
class UnifiedFinding:
    """统一格式的代码审查发现类"""
    priority: str       # 严重/一般/轻微
    issue_type: str     # 内存泄露/超时处理不足/安全隐患等（由AI分析）
    location: str       # 文件路径:行号
    description: str    # 问题详细说明
    suggestion: str     # 修复建议（由AI生成）

    def to_dict(self) -> dict:
        """转换为字典格式，用于报告生成"""
        return {
            "优先级": self.priority,
            "问题类型": self.issue_type,
            "位置": self.location,
            "说明": self.description,
            "修复建议": self.suggestion
        }
```

#### 2. AI 处理模块

```python
class UnifiedFindingProcessor:
    """负责将原始发现转换为统一格式的AI处理模块"""

    def __init__(self, config):
        self.ai_client = AI处理引擎（使用现有AI客户端）

    def process_findings(self,
                        local_findings: List[RuleFinding],
                        ai_findings: List[AIReviewFinding]) -> List[UnifiedFinding]:
        """
        处理所有原始发现，使用AI分析问题类型和生成修复建议
        """
        pass
```

### 报告格式示例

#### 文本报告示例（Markdown 表格格式）

```
代码审查报告
============

| 优先级 | 问题类型       | 位置                  | 说明                     | 修复建议                     |
|--------|---------------|-----------------------|--------------------------|------------------------------|
| 严重   | 内存泄露       | MainActivity.java:120 | Handler 持有外部类引用   | 使用静态内部类 + WeakReference |
| 一般   | 超时处理不足   | ApiClient.java:85     | 网络请求超时设置过短     | 增加超时时间到 30 秒         |
| 轻微   | 代码风格       | Utils.java:42         | 未使用 try-with-resources| 改用 try-with-resources 语法 |
```

#### HTML 报告示例

将使用 Bootstrap 样式的响应式表格：

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
  </tbody>
</table>
```

#### JSON 报告示例

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

## 实现计划

### 阶段 1：核心类创建
1. 创建 `UnifiedFinding` 数据类
2. 创建 `UnifiedFindingProcessor` 处理类
3. 实现原始发现到统一格式的转换逻辑

### 阶段 2：AI 处理
1. 设计并实现 AI 问题分类提示词
2. 设计并实现 AI 修复建议提示词
3. 实现对本地规则发现的 AI 分析功能
4. 实现对 AI 发现的规范化处理

### 阶段 3：报告生成器
1. 重构 TextReporter，输出 Markdown 表格
2. 重构 HtmlReporter，输出 Bootstrap 表格
3. 重构 JsonReporter，输出统一格式的 JSON
4. 保持报告生成的完整性和可读性

### 阶段 4：集成与测试
1. 集成到主程序流程中
2. 单元测试
3. 集成测试
4. 边界情况处理

## 优势

### 开发便利性保持不变
- ✅ 现有规则编写方式完全不变
- ✅ 规则开发时还是继承 BaseRule
- ✅ 新增语言规则只需添加对应目录
- ✅ 动态加载机制自动发现新规则

### 用户体验提升
- ✅ 更清晰的问题分类
- ✅ 优先级明确，便于处理
- ✅ 表格格式，易于阅读和分析
- ✅ AI 智能分析问题类型和修复建议

### 扩展性保障
- ✅ 规则架构设计良好，扩展性高
- ✅ 未来语言支持轻松添加
- ✅ AI 处理模块模块化设计
