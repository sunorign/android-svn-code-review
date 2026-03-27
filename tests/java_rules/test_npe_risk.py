from src.local_rules.java_rules.npe_risk import NPERiskRule
from src.diff_parser import FileDiff, DiffChange


def test_finds_to_string():
    rule = NPERiskRule()
    change = DiffChange(line_number=10, content="        String str = var.toString();", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert ".toString()" in findings[0].message


def test_finds_equals():
    rule = NPERiskRule()
    change = DiffChange(line_number=10, content='        if (var.equals("test")) {', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert ".equals(" in findings[0].message


def test_finds_charAt():
    rule = NPERiskRule()
    change = DiffChange(line_number=10, content="        char c = var.charAt(0);", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert ".charAt(" in findings[0].message


def test_finds_length():
    rule = NPERiskRule()
    change = DiffChange(line_number=10, content="        if (var.length() > 0) {", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert ".length()" in findings[0].message


def test_ignores_null_check_context():
    rule = NPERiskRule()
    change = DiffChange(line_number=10, content="        if (var != null) { var.toString(); }", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_ignores_comments():
    rule = NPERiskRule()
    change = DiffChange(line_number=10, content="        // var.toString();", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_ignores_in_strings():
    rule = NPERiskRule()
    change = DiffChange(line_number=10, content="        String example = \"var.toString()\";", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_check_full_file():
    rule = NPERiskRule()
    file_content = """
    public class TestClass {
        public void testMethod() {
            String str = var.toString();
            if (var.equals("test")) {
                // Do something
            }
            char c = var.charAt(0);
            if (var.length() > 0) {
                // Do something else
            }

            // This is a comment: var.toString();
            String example = "var.equals(\"test\")";
        }
    }
    """
    findings = rule.check_full_file("Test.java", file_content)

    assert len(findings) == 4
    severities = [f.severity for f in findings]
    assert all(severity == "WARNING" for severity in severities)