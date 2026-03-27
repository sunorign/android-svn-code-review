#!/usr/bin/env python3
"""Test the full code review flow."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import main
import subprocess
import unittest.mock

def test_full_flow():
    """Test the main function with mocked SVN diff."""
    print("Testing full code review flow...")

    # Mock SVN diff output
    mock_diff = """Index: src/test.java
--- src/test.java	(revision 123)
+++ src/test.java	(working copy)
@@ -1,3 +1,4 @@
 public class Test {
+    public static void main(String[] args) {
         System.out.println("Hello");
+    }
 }
"""

    # Mock subprocess.check_output
    with unittest.mock.patch('subprocess.check_output') as mock_check_output:
        mock_check_output.return_value = mock_diff

        # Mock tkinter messagebox
        with unittest.mock.patch('tkinter.messagebox.askyesno') as mock_askyesno:
            mock_askyesno.return_value = False  # Don't run full review

            # Mock get_ai_client
            with unittest.mock.patch('src.main.get_ai_client') as mock_get_ai_client:
                mock_get_ai_client.return_value = None  # No AI client

                # Mock load_all_rules to return empty list
                with unittest.mock.patch('src.main.load_all_rules') as mock_load_rules:
                    mock_load_rules.return_value = []

                    try:
                        exit_code = main()
                        print(f"OK: Main function completed with exit code: {exit_code}")
                        return exit_code == 0
                    except Exception as e:
                        print(f"ERROR: Main function failed: {e}")
                        import traceback
                        print(traceback.format_exc())
                        return False

def test_with_blocking_issues():
    """Test main function with blocking issues."""
    print("\nTesting flow with blocking issues...")

    # Mock SVN diff output
    mock_diff = """Index: src/test.java
--- src/test.java	(revision 123)
+++ src/test.java	(working copy)
@@ -1,3 +1,4 @@
 public class Test {
+    System.out.println("debug log");
         System.out.println("Hello");
 }
"""

    # Mock subprocess.check_output
    with unittest.mock.patch('subprocess.check_output') as mock_check_output:
        mock_check_output.return_value = mock_diff

        # Mock tkinter messagebox
        with unittest.mock.patch('tkinter.messagebox.askyesno') as mock_askyesno:
            mock_askyesno.return_value = False  # Don't run full review

            # Mock load_all_rules to return a rule that finds blocking issues
            from src.local_rules.base_rule import BaseRule, RuleFinding

            class MockBlockingRule(BaseRule):
                @property
                def name(self):
                    return "MockBlockingRule"

                @property
                def description(self):
                    return "Mock rule that finds blocking issues"

                def check_diff(self, file_diff, change=None):
                    return [RuleFinding(
                        file_path=file_diff.file_path,
                        line_number=2,
                        rule_name=self.name,
                        message="Found debug logging",
                        severity="BLOCK"
                    )]

                def check_full_file(self, file_path, content):
                    return []

            with unittest.mock.patch('src.main.load_all_rules') as mock_load_rules:
                mock_load_rules.return_value = [MockBlockingRule()]

                try:
                    exit_code = main()
                    print(f"OK: Main function completed with exit code: {exit_code}")
                    return exit_code == 1  # Should return 1 for blocking issues
                except Exception as e:
                    print(f"ERROR: Main function failed: {e}")
                    import traceback
                    print(traceback.format_exc())
                    return False

if __name__ == "__main__":
    print("=" * 50)
    print("Full Flow Test")
    print("=" * 50)

    success = True

    # Test normal flow
    if not test_full_flow():
        success = False

    # Test blocking issues flow
    if not test_with_blocking_issues():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
    print("=" * 50)

    sys.exit(0 if success else 1)
