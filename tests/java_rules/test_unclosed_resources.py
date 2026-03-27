from src.local_rules.java_rules.unclosed_resources import UnclosedResourcesRule
from src.diff_parser import FileDiff, DiffChange


def test_finds_cursor_resource():
    rule = UnclosedResourcesRule()
    change = DiffChange(line_number=10, content="        Cursor cursor = new Cursor(cursorFactory);", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "Cursor" in findings[0].message


def test_finds_file_input_stream():
    rule = UnclosedResourcesRule()
    change = DiffChange(line_number=10, content="        FileInputStream fis = new FileInputStream(filePath);", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "FileInputStream" in findings[0].message


def test_finds_file_output_stream():
    rule = UnclosedResourcesRule()
    change = DiffChange(line_number=10, content="        FileOutputStream fos = new FileOutputStream(outputFile);", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "FileOutputStream" in findings[0].message


def test_finds_connection():
    rule = UnclosedResourcesRule()
    change = DiffChange(line_number=10, content="        Connection conn = new Connection(databaseUrl);", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "Connection" in findings[0].message


def test_finds_statement():
    rule = UnclosedResourcesRule()
    change = DiffChange(line_number=10, content="        Statement stmt = new Statement(conn);", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "Statement" in findings[0].message


def test_finds_stream_generic():
    rule = UnclosedResourcesRule()
    change = DiffChange(line_number=10, content="        Stream<String> stream = getStream();", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "Stream" in findings[0].message


def test_ignores_comments():
    rule = UnclosedResourcesRule()
    change = DiffChange(line_number=10, content="        // new Cursor(cursorFactory);", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_ignores_in_strings():
    rule = UnclosedResourcesRule()
    change = DiffChange(line_number=10, content="        String example = \"new Cursor(cursorFactory)\";", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_check_full_file():
    rule = UnclosedResourcesRule()
    file_content = """
    public class TestClass {
        public void testMethod() {
            Cursor cursor = new Cursor(cursorFactory);
            FileInputStream fis = new FileInputStream(filePath);
            FileOutputStream fos = new FileOutputStream(outputFile);
            Connection conn = new Connection(databaseUrl);
            Statement stmt = new Statement(conn);
            Stream<String> stream = getStream();

            // This is a comment: new Cursor(cursorFactory);
            String example = "new Connection(databaseUrl)";
        }
    }
    """
    findings = rule.check_full_file("Test.java", file_content)

    assert len(findings) == 6
    severities = [f.severity for f in findings]
    assert all(severity == "WARNING" for severity in severities)