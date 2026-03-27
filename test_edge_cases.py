from src.local_rules.java_rules.debug_logging import DebugLoggingRule


def test_edge_cases():
    rule = DebugLoggingRule()

    # 测试各种边界情况
    file_content = """
    public class TestClass {
        public void testMethod() {
            // 单行注释中的System.out.println - 不应匹配
            /* 多行注释中的System.err.println - 不应匹配 */
            String s1 = "System.out.println(\"字符串中的调试日志\");"; // 字符串中的内容 - 不应匹配
            String s2 = "Log.d(\"tag\", \"message\");"; // 字符串中的Log.d - 不应匹配

            // 真正的调试代码 - 应该匹配
            System.out.println("debug");
            Log.d("TAG", "debug");
            System.err.println("error");
            Log.v("TAG", "verbose");
        }
    }
    """

    findings = rule.check_full_file("Test.java", file_content)

    # 应该只匹配4个真正的调试语句
    assert len(findings) == 4, f"Expected 4 findings, got {len(findings)}"

    # 检查所有找到的都是真正的调试语句
    found = {}
    for f in findings:
        found[f.message.split('`')[1]] = True

    assert "System.out.println" in found
    assert "Log.d" in found
    assert "System.err.println" in found
    assert "Log.v" in found

    print("所有测试通过！")


if __name__ == "__main__":
    test_edge_cases()