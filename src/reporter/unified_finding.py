from dataclasses import dataclass
from typing import Optional


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
