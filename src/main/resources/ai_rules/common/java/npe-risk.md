# 规则名
空指针风险检查

# 标签
null, npe, pointer, kotlin, java

# 描述
识别代码中可能出现空指针异常的场景：
- 多级可空链式调用：obj?.let?.map?.apply
- !! 非空断言的潜在风险
- 可空类型变量未判空直接使用
- 平台类型从 Java 来，Kotlin 当作非空处理

分析是否存在肯定会触发 NPE 的代码，如果有报告 BLOCK，有潜在风险报告 WARNING。
