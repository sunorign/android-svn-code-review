from src.local_rules.java_rules.hardcoded_secrets import HardcodedSecretsRule
from src.diff_parser import FileDiff, DiffChange


def test_finds_password_in_string():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String password = "mysecret123";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"


def test_finds_api_key():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String apiKey = "AKIAXXXX";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 1


def test_finds_secret_in_string():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String secret = "supersecret";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 1


def test_finds_token_in_string():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String token = "jwt-token-123";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 1


def test_finds_api_key_with_underscore():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String api_key = "AKIA123456";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 1


def test_finds_api_key_with_dash():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String api-key = "AKIA789012";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 1


def test_skips_commented_out_password():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='// String password = "shouldnotfind";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_skips_multiline_comment_start():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='/* String password = "shouldnotfind";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_skips_password_in_middle_of_line_comment():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String x = "hello"; // password = "secret"', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_full_file_detection():
    rule = HardcodedSecretsRule()
    content = """
public class Test {
    public void method() {
        String password = "mysecret123";
        String apiKey = "AKIAXXXX";
        String secret = "supersecret";
        String token = "jwt-token-123";
        // String should_not_find = "password";
    }
}
"""
    findings = rule.check_full_file("Test.java", content)
    assert len(findings) == 4


def test_finds_base64_secret():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String apiKey = "AKIA1234+/=";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 1


def test_finds_secret_with_dash_and_underscore():
    rule = HardcodedSecretsRule()
    change = DiffChange(10, content='String secret_key = "secret-123_abc";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 1


def test_skips_password_in_string_literal():
    rule = HardcodedSecretsRule()
    # This should not find anything because password is inside a string literal
    change = DiffChange(10, content=r'String message = "password = \"secret\"";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_skips_pattern_in_middle_of_word():
    rule = HardcodedSecretsRule()
    # Should not match "password" inside "mypassword123"
    change = DiffChange(10, content='String mypassword123 = "value";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0
