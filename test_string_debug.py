from src.local_rules.java_rules.npe_risk import NPERiskRule
from src.diff_parser import FileDiff, DiffChange

def test_string_detection():
    rule = NPERiskRule()
    content1 = '        String example = "var.toString()";'
    print("Testing line:", repr(content1))

    # Check if ".toString()" is matched
    for pattern, display_str in rule.NPE_PATTERNS:
        match = pattern.search(content1)
        if match:
            print(f"Found match: {display_str} at positions {match.start()}:{match.end()}")
            is_in_string = rule._is_pattern_in_string(content1, match.start(), match.end())
            print(f"  Is in string? {is_in_string}")

    change = DiffChange(line_number=10, content=content1, is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    print(f"Findings count: {len(findings)}")
    for finding in findings:
        print(f"  Finding: {finding.message}")

test_string_detection()