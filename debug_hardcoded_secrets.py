from src.local_rules.java_rules.hardcoded_secrets import HardcodedSecretsRule
from src.diff_parser import FileDiff, DiffChange
import sys
sys.path.append('D:/Documents/Projects/projects_pycharm/superpowertest/src/local_rules/java_rules')
from hardcoded_secrets import SECRET_PATTERNS

def debug_test():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String message = "password = \"secret\"";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    print("Findings count:", len(findings))
    if findings:
        print(f"Finding: {findings[0]}")

    # Debug step by step
    content = change.content
    print("\nOriginal content:", repr(content))

    content_without_comments = rule._remove_comments(content)
    print("\nWithout comments:", repr(content_without_comments))

    for pattern in SECRET_PATTERNS:
        match = pattern.search(content_without_comments)
        if match:
            print(f"\nPattern found: {pattern.pattern}")
            print(f"Match: {match.group()}")
            print(f"Match positions: start={match.start()}, end={match.end()}")

            # Check if it's in string
            is_in_string = rule._is_pattern_in_string(content_without_comments, match.start(), match.end())
            print(f"In string literal: {is_in_string}")

debug_test()