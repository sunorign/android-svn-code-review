# 规则名
调试日志检查

# 标签
debug, log, logging, java

# 描述
检查代码中残留的调试日志代码，这些代码应该在发布前移除。

需要检查的模式包括：
- System.out.println
- Log.d / Log.v（调试级别日志）

Log.i / Log.w / Log.e 是正式日志，不需要报告。

发现调试日志报告 BLOCK 级别问题，必须移除。
