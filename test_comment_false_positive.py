from src.local_rules.java_rules.debug_logging import DebugLoggingRule


def test_comments_and_strings():
    rule = DebugLoggingRule()

    # 测试注释中的调试日志（不应该被匹配）
    file_content = """
    public class TestClass {
        public void testMethod() {
            // 这是一行注释 System.out.println("test");
            /* 多行注释
               System.err.println("test");
             */
            String s = "System.out.println(\"not a real call\");";

            // 真正的调试代码
            System.out.println("real debug");
        }
    }
    """

    findings = rule.check_full_file("Test.java", file_content)

    # 应该只匹配1个真正的调用，而不是3个
    assert len(findings) == 1
    assert "real debug" in findings[0].code_snippet