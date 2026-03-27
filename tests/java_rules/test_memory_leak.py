from src.local_rules.java_rules.memory_leak import MemoryLeakRule
from src.diff_parser import FileDiff, DiffChange


def test_finds_on_click_listener():
    rule = MemoryLeakRule()
    change = DiffChange(line_number=10, content="    private class MyClickListener implements View.OnClickListener {", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "OnClickListener" in findings[0].message


def test_finds_runnable():
    rule = MemoryLeakRule()
    change = DiffChange(line_number=10, content="    private class MyRunnable implements Runnable {", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "Runnable" in findings[0].message


def test_finds_on_touch_listener():
    rule = MemoryLeakRule()
    change = DiffChange(line_number=10, content="    private class MyTouchListener implements View.OnTouchListener {", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "OnTouchListener" in findings[0].message


def test_finds_on_long_click_listener():
    rule = MemoryLeakRule()
    change = DiffChange(line_number=10, content="    private class MyLongClickListener implements View.OnLongClickListener {", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "OnLongClickListener" in findings[0].message


def test_finds_async_task():
    rule = MemoryLeakRule()
    change = DiffChange(line_number=10, content="    private class MyAsyncTask extends AsyncTask<Void, Void, Void> {", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "AsyncTask" in findings[0].message


def test_ignores_comments():
    rule = MemoryLeakRule()
    change = DiffChange(line_number=10, content="    // private class MyClickListener implements View.OnClickListener {", is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_ignores_in_strings():
    rule = MemoryLeakRule()
    change = DiffChange(line_number=10, content='    String example = "private class MyRunnable implements Runnable";', is_added=True, is_removed=False)
    findings = rule.check_diff(FileDiff("Test.java", False, False), change)
    assert len(findings) == 0


def test_check_full_file():
    rule = MemoryLeakRule()
    file_content = """
    public class MainActivity extends AppCompatActivity {

        private TextView textView;

        @Override
        protected void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            setContentView(R.layout.activity_main);
            textView = findViewById(R.id.text_view);
        }

        // This is also a memory leak risk
        private class MyRunnable implements Runnable {
            @Override
            public void run() {
                // Do background work
            }
        }

        // This is a memory leak risk - named inner class
        private class MyClickListener implements View.OnClickListener {
            @Override
            public void onClick(View v) {
                // Handle click
            }
        };

        // This is a static inner class (safe)
        private static class MyStaticRunnable implements Runnable {
            @Override
            public void run() {
                // Do background work (safe)
            }
        }
    }
    """
    findings = rule.check_full_file("MainActivity.java", file_content)

    assert len(findings) == 2
    severities = [f.severity for f in findings]
    assert all(severity == "WARNING" for severity in severities)