from src.diff_parser import DiffParser, DiffChange, FileDiff


def test_parse_simple_diff():
    diff_text = """Index: src/com/example/Main.java
===================================================================
--- src/com/example/Main.java	(revision 123)
+++ src/com/example/Main.java	(working copy)
@@ -10,6 +10,8 @@
     public void doSomething() {
+        System.out.println("debug");
+        // todo: remove this
         somethingElse();
     }
"""
    parser = DiffParser(diff_text)
    file_diffs = parser.parse()

    assert len(file_diffs) == 1
    assert file_diffs[0].file_path == "src/com/example/Main.java"
    assert file_diffs[0].is_new_file is False
    assert len(file_diffs[0].changes) == 2  # two lines added


def test_parse_new_file():
    diff_text = """Index: NewFile.java
===================================================================
--- NewFile.java	(revision 0)
+++ NewFile.java	(working copy)
@@ -0,0 +1,5 @@
+package com.example;
+
+public class NewFile {
+}
"""
    parser = DiffParser(diff_text)
    file_diffs = parser.parse()

    assert len(file_diffs) == 1
    assert file_diffs[0].is_new_file is True
    assert len(file_diffs[0].added_lines) == 4
