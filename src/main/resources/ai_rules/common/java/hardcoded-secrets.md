# 规则名
硬编码敏感信息

# 标签
security, secret, password, key, hardcode, java

# 描述
检测代码中硬编码的密码、密钥、API Key、令牌等敏感信息。

这些敏感信息硬编码在代码中会导致安全风险，应该从配置文件或环境变量读取。

发现硬编码敏感信息报告 BLOCK 级别问题。
