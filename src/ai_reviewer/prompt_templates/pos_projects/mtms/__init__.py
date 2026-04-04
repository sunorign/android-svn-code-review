"""MTMS设备管理项目 - AI提示词配置

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
    # "mtms-update-check-diff.md",
    # "mtms-log-collection-full.md",
]
