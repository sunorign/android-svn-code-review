from src.local_rules.android_rules.hardcoded_urls import HardcodedUrlsRule
from src.diff_parser import FileDiff, DiffChange


def test_finds_hardcoded_url():
    rule = HardcodedUrlsRule()
    change = DiffChange(line_number=10, content='        String url = "https://api.example.com/v1/data";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "https://api.example.com/v1/data" in findings[0].message


def test_finds_hardcoded_ip():
    rule = HardcodedUrlsRule()
    change = DiffChange(line_number=10, content='        String ip = "http://192.168.1.100:8080/api";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "http://192.168.1.100:8080/api" in findings[0].message


def test_ignores_localhost():
    rule = HardcodedUrlsRule()
    change = DiffChange(line_number=10, content='        String url = "http://localhost:8080/api";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 0


def test_ignores_localhost_ip():
    rule = HardcodedUrlsRule()
    change = DiffChange(line_number=10, content='        String url = "https://127.0.0.1:3000";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 0


def test_ignores_comments():
    rule = HardcodedUrlsRule()
    change = DiffChange(line_number=10, content='        // String url = "https://api.example.com/v1/data";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 0


def test_detects_url_in_string():
    rule = HardcodedUrlsRule()
    change = DiffChange(line_number=10, content='        String s = "This is a test https://api.example.com";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert "https://api.example.com" in findings[0].message


def test_check_full_file():
    rule = HardcodedUrlsRule()
    file_content = """
    public class TestClass {
        public void testMethod() {
            String url1 = "https://api.example.com/v1/data";
            String ip = "http://192.168.1.100:8080/api";
            String localhost = "http://localhost:8080/api";
            String localip = "https://127.0.0.1:3000";
        }
    }
    """
    findings = rule.check_full_file("Test.java", file_content)

    assert len(findings) == 2
    severities = [f.severity for f in findings]
    assert all(severity == "WARNING" for severity in severities)
