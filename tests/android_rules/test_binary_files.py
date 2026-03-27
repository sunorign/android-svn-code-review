from src.local_rules.android_rules.binary_files import BinaryFilesRule
from src.diff_parser import FileDiff, DiffChange


def test_finds_apk_file():
    rule = BinaryFilesRule()
    file_diff = FileDiff("app-debug.apk", False, False)
    change = DiffChange(line_number=1, content="PK\x03\x04", is_added=True, is_removed=False)
    findings = rule.check_diff(file_diff, change)

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
    assert "Binary file" in findings[0].message


def test_finds_dex_file():
    rule = BinaryFilesRule()
    file_diff = FileDiff("classes.dex", False, False)
    change = DiffChange(line_number=1, content="dex\n035", is_added=True, is_removed=False)
    findings = rule.check_diff(file_diff, change)

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
    assert "Binary file" in findings[0].message


def test_finds_jar_file():
    rule = BinaryFilesRule()
    file_diff = FileDiff("library.jar", False, False)
    change = DiffChange(line_number=1, content="PK\x03\x04", is_added=True, is_removed=False)
    findings = rule.check_diff(file_diff, change)

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
    assert "Binary file" in findings[0].message


def test_finds_binary_content():
    rule = BinaryFilesRule()
    file_diff = FileDiff("unknown.bin", False, False)
    # 包含空字节的内容通常是二进制文件
    change = DiffChange(line_number=1, content="\x00\x01\x02\x03\x04\x05", is_added=True, is_removed=False)
    findings = rule.check_diff(file_diff, change)

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
    assert "Binary file" in findings[0].message


def test_check_full_file_apk():
    rule = BinaryFilesRule()
    findings = rule.check_full_file("app-release.apk", "PK\x03\x04")

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"


def test_check_full_file_jar():
    rule = BinaryFilesRule()
    findings = rule.check_full_file("utils.jar", "PK\x03\x04")

    assert len(findings) == 1
    assert findings[0].severity == "BLOCK"
