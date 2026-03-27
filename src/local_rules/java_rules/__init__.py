from src.local_rules.java_rules.debug_logging import DebugLoggingRule
from src.local_rules.java_rules.hardcoded_secrets import HardcodedSecretsRule
from src.local_rules.java_rules.unclosed_resources import UnclosedResourcesRule
from src.local_rules.java_rules.npe_risk import NPERiskRule
from src.local_rules.java_rules.memory_leak import MemoryLeakRule

# List of all Java rules
JAVARULES = [
    DebugLoggingRule(),
    HardcodedSecretsRule(),
    UnclosedResourcesRule(),
    NPERiskRule(),
    MemoryLeakRule(),
]