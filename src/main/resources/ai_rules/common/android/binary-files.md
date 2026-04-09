# 规则名
二进制文件检查

# 标签
binary, apk, dex, aar, so, file, android

# 描述
检查代码仓库中是否提交了 .apk / .dex / .aar / .so 等二进制文件。

这些文件不应该提交到代码仓库，会导致仓库体积膨胀。

发现二进制文件报告 BLOCK 级别问题，必须移除。