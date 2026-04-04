"""MTMS设备管理软件项目 - 启用规则配置"""

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
PROJECT_DISPLAY_NAME = "MTMS设备管理"

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
    # 如需添加 MTMS 特有规则，在这里导入并添加实例
]
