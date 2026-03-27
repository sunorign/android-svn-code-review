#!/usr/bin/env python3
"""Test script for main entry point validation."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")

    try:
        from src.main import main, generate_reports
        print("OK: Main module imported successfully")
    except Exception as e:
        print(f"ERROR: Failed to import main module: {e}")
        return False

    try:
        from src.reporter import TextReporter, HTMLReporter, JSONReporter
        print("OK: Reporters imported successfully")
    except Exception as e:
        print(f"ERROR: Failed to import reporters: {e}")
        return False

    try:
        from src.diff_parser import DiffParser, FileDiff
        print("OK: Diff parser imported successfully")
    except Exception as e:
        print(f"ERROR: Failed to import diff parser: {e}")
        return False

    try:
        from src.scanner import FileScanner
        print("OK: File scanner imported successfully")
    except Exception as e:
        print(f"ERROR: Failed to import file scanner: {e}")
        return False

    try:
        from src.local_rules import load_all_rules
        print("OK: Local rules imported successfully")
    except Exception as e:
        print(f"ERROR: Failed to import local rules: {e}")
        return False

    try:
        from src.config import Config
        print("OK: Config module imported successfully")
    except Exception as e:
        print(f"ERROR: Failed to import config: {e}")
        return False

    print("All imports passed!")
    return True

def test_scanner_scan_method():
    """Test if FileScanner has scan method."""
    print("\nTesting FileScanner.scan method...")

    from src.scanner import FileScanner
    from src.diff_parser import FileDiff, DiffChange

    scanner = FileScanner()
    if hasattr(scanner, 'scan'):
        print("OK: FileScanner has scan method")

        # Test with dummy file diffs
        dummy_diffs = [
            FileDiff(file_path="src/test.java", is_new_file=True, is_deleted=False, changes=[
                DiffChange(line_number=1, content="public class Test {", is_added=True, is_removed=False)
            ]),
            FileDiff(file_path="libs/test.jar", is_new_file=True, is_deleted=False, changes=[
                DiffChange(line_number=1, content="Binary file", is_added=True, is_removed=False)
            ]),
            FileDiff(file_path="build/output.apk", is_new_file=True, is_deleted=False, changes=[
                DiffChange(line_number=1, content="Binary file", is_added=True, is_removed=False)
            ])
        ]

        scan_results = scanner.scan(dummy_diffs)
        print(f"OK: Scan method returns: {type(scan_results)}")
        print(f"  - file_diffs: {len(scan_results['file_diffs'])}")
        print(f"  - libs_notifications: {len(scan_results['libs_notifications'])}")

        return True
    else:
        print("ERROR: FileScanner missing scan method")
        return False

def test_diff_parser():
    """Test DiffParser initialization and parsing."""
    print("\nTesting DiffParser...")

    from src.diff_parser import DiffParser

    sample_diff = """Index: src/test.java
--- src/test.java	(revision 123)
+++ src/test.java	(working copy)
@@ -1,3 +1,4 @@
 public class Test {
+    public static void main(String[] args) {
         System.out.println("Hello");
+    }
 }
"""

    try:
        parser = DiffParser(sample_diff)
        file_diffs = parser.parse()
        print("OK: Diff parser initialized and parsed successfully")
        print(f"  - Number of file diffs: {len(file_diffs)}")

        if file_diffs:
            print(f"  - File: {file_diffs[0].file_path}")
            print(f"  - Changes: {len(file_diffs[0].changes)}")

        return True
    except Exception as e:
        print(f"ERROR: Diff parser error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_reporter_generate():
    """Test if reporters have generate method."""
    print("\nTesting reporters...")

    from src.reporter import TextReporter, HTMLReporter, JSONReporter
    from src.local_rules.base_rule import RuleFinding

    reporters = [
        TextReporter(),
        HTMLReporter(),
        JSONReporter()
    ]

    all_passed = True

    for reporter in reporters:
        reporter_name = reporter.__class__.__name__
        if hasattr(reporter, 'generate'):
            print(f"OK: {reporter_name} has generate method")

            # Test with dummy data
            dummy_findings = [
                RuleFinding(
                    file_path="src/test.java",
                    line_number=5,
                    rule_name="DebugLoggingRule",
                    message="Debug logging found",
                    severity="WARNING",
                    code_snippet="System.out.println(\"Debug info\");"
                )
            ]

            dummy_meta = {
                "timestamp": "2025-03-27T10:30:00",
                "mode": "diff-only",
                "file_count": 1,
                "has_block_issues": False
            }

            try:
                report_path = reporter.generate(dummy_findings, dummy_meta)
                print(f"OK: Generated report at: {report_path}")

                # Verify file was created
                if os.path.exists(report_path):
                    print(f"OK: Report file exists (size: {os.path.getsize(report_path)} bytes)")
                    os.remove(report_path)  # Clean up
                else:
                    print(f"ERROR: Report file not created")

            except Exception as e:
                print(f"ERROR: {reporter_name} generate method failed: {e}")
                import traceback
                print(traceback.format_exc())
                all_passed = False
        else:
            print(f"ERROR: {reporter_name} missing generate method")
            all_passed = False

    return all_passed

def test_load_rules():
    """Test loading all rules."""
    print("\nTesting load_all_rules...")

    from src.local_rules import load_all_rules

    try:
        rules = load_all_rules()
        print(f"OK: Loaded {len(rules)} rules")

        if rules:
            for i, rule in enumerate(rules[:5], 1):  # Show first 5 rules
                print(f"  - {i}. {rule.name}")

            if len(rules) > 5:
                print(f"  - ... and {len(rules) - 5} more")

        return True
    except Exception as e:
        print(f"ERROR: Failed to load rules: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main_test():
    """Main test function."""
    print("=" * 50)
    print("SuperPower Code Review Main Entry Point Test")
    print("=" * 50)

    tests = [
        test_imports,
        test_scanner_scan_method,
        test_diff_parser,
        test_reporter_generate,
        test_load_rules
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"ERROR: Test failed: {e}")
            import traceback
            print(traceback.format_exc())
            failed += 1

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    # Cleanup generated directory
    output_dir = "code-review-output"
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(output_dir)
        print(f"\nCleaned up {output_dir}")

    return failed == 0

if __name__ == "__main__":
    success = main_test()
    sys.exit(0 if success else 1)
