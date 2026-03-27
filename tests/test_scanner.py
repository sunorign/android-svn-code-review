from src.diff_parser import FileDiff
from src.scanner import FileScanner, ScanResult


def test_should_ignore_build_dir():
    scanner = FileScanner()
    result = scanner.should_check_file("app/build/generated/some.java")
    assert result.should_ignore is True
    assert result.is_libs_change is False


def test_should_ignore_generated():
    scanner = FileScanner()
    result = scanner.should_check_file("app/src/generated/File.java")
    assert result.should_ignore is True


def test_libs_directory_change():
    scanner = FileScanner()
    result = scanner.should_check_file("libs/mylib.jar")
    assert result.should_ignore is True
    assert result.is_libs_change is True


def test_should_check_source_file():
    scanner = FileScanner()
    result = scanner.should_check_file("app/src/main/java/com/example/Main.java")
    assert result.should_ignore is False
    assert result.is_libs_change is False
    assert scanner.should_check_extension("app/src/main/java/com/example/Main.java") is True