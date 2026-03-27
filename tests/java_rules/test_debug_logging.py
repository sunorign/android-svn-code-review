from src.local_rules.java_rules.debug_logging import DebugLoggingRule
from src.diff_parser import FileDiff, DiffChange


def test_finds_system_out():
    rule = DebugLoggingRule()
    change = DiffChange(line_number=10, content="        System.out.println(\"debug\");", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
    assert "System.out.println" in findings[0].message


def test_finds_system_err():
    rule = DebugLoggingRule()
    change = DiffChange(line_number=10, content="        System.err.println(\"error debug\");", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
    assert "System.err.println" in findings[0].message


def test_finds_log_d():
    rule = DebugLoggingRule()
    change = DiffChange(line_number=10, content="        Log.d(TAG, \"debug msg\");", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
    assert "Log.d" in findings[0].message


def test_finds_log_v():
    rule = DebugLoggingRule()
    change = DiffChange(line_number=10, content="        Log.v(TAG, \"verbose debug\");", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
    assert "Log.v" in findings[0].message


def test_check_full_file():
    rule = DebugLoggingRule()
    file_content = """
    public class TestClass {
        public void testMethod() {
            System.out.println("debug");
            Log.d(TAG, "debug message");
            System.err.println("error log");
            Log.v(TAG, "verbose log");
        }
    }
    """
    findings = rule.check_full_file("Test.java", file_content)

    assert len(findings) == 4
    severities = [f.severity for f in findings]
    assert all(severity == "BLOCK" for severity in severities)