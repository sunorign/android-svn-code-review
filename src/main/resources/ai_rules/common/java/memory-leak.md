# 规则名
内存泄漏风险

# 标签
memory, leak, inner-class, android, java

# 描述
检测可能导致内存泄漏的代码：
- 非静态内部类持有外部 Activity/Context 引用
- 静态变量持有 Activity 实例
- Handler post 延迟消息持有 Context
- 未注销的监听器

发现潜在内存泄漏报告 WARNING 级别问题。
