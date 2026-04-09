# 规则名
未关闭资源检查

# 标签
resource, leak, io, cursor, stream, connection, java

# 描述
检查代码中 Cursor、InputStream、OutputStream、Connection 等资源是否正确关闭。

重点关注：
- 打开资源后，在所有退出路径是否都有 close() 调用
- 是否使用 try-with-resources 语法自动关闭
- 异常处理分支是否遗漏关闭

发现未关闭资源报告 WARNING 级别问题。
