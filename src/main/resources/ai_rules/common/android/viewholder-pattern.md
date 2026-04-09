# 规则名
ViewHolder 模式检查

# 标签
ui, listview, recyclerview, viewholder, pattern, android

# 描述
检查 ListView/RecyclerView 中是否正确使用 ViewHolder 模式。

错误做法：getView/onBindViewHolder 中每次都调用 findViewById
正确做法：使用 ViewHolder 缓存 findViewById 结果

未正确使用 ViewHolder 模式报告 WARNING 级别问题，影响滑动性能。