# 自定义输出目录功能 - 设计规格

## 需求背景

当前 GUI 模式下，输出报告目录固定为 `~/code-review-output`，用户无法自定义。对于使用打包后的 exe 的用户，不清楚默认路径在哪里，也不方便把报告保存到指定位置。

需要在 GUI 中增加自定义输出目录功能，并且设置需要持久化保存。

## 设计方案

### 1. 新增 AppSettings 数据类和加载器

**文件位置**：`src/main/kotlin/com/codereview/core/AppSettings.kt`

```kotlin
@Serializable
data class AppSettings(
    val outputDirectory: String? = null  // null = use default ~/code-review-output
)

object AppSettingsLoader {
    private val json = Json { prettyPrint = true }

    fun loadSettings(): AppSettings
    fun saveSettings(settings: AppSettings)
    fun getUserConfigFile(): File = File(System.getProperty("user.home"), ".code-review/app_settings.json")
}
```

- 遵循现有的 `ScanSettingsLoader` 相同的模式，`AppSettings` 和 `AppSettingsLoader` 在同一文件中
- 使用 Kotlinx Serialization JSON 序列化
- 配置文件保存在 `~/.code-review/app_settings.json`
- `saveSettings()` 会确保 `~/.code-review/` 目录存在，不存在则创建

### 2. UI 修改：ScanSettingsDialog

在"扫描设置"对话框底部添加输出目录选择区域：

- **文本框**：显示当前选择的输出目录，只读不可编辑
- **浏览...按钮**：点击打开系统目录选择对话框
- **使用默认路径**复选框：勾选后禁用选择，使用默认路径

UI 布局顺序：
1. 扫描模式选择（保持不变）
2. Diff 粒度选择（保持不变）
3. 输出目录选择（新增）

### 3. 行为逻辑

- 如果 `outputDirectory` 为 `null` 或为空字符串，使用默认 `~/code-review-output`
- 如果用户选择了自定义目录，**必须使用绝对路径**，保存到设置中
- 保存设置前验证目录：
  - 检查目录是否存在，不存在尝试创建
  - 检查目录是否有写权限
  - 验证失败显示错误消息，不允许保存
- 保存设置后，重启应用自动恢复用户选择
- 向后兼容：原有用户配置文件不影响，加载时会使用默认值

### 4. MainScreen 修改

- 在开始审查时，从 `AppSettingsLoader` 加载自定义输出目录设置
- 如果有自定义目录，使用该目录生成报告文件
- 生成报告前确保输出目录存在（调用 `mkdirs()`）
- 在结果文本中**显示实际使用的输出目录完整路径**，方便用户查找
- 原有逻辑保持不变，只是输出目录来源改变

### 5. 默认值

| 场景 | 默认值 |
|------|--------|
| 新安装首次启动 | `null` → 使用 `~/code-review-output` |
| 用户自定义后 | 保存用户选择 |

## 代码修改清单

1. **新增** `src/main/kotlin/com/codereview/core/AppSettings.kt` - 应用设置数据类和加载器
2. **修改** `src/main/kotlin/com/codereview/gui/ScanSettingsDialog.kt` - 添加输出目录选择 UI 和验证
3. **修改** `src/main/kotlin/com/codereview/gui/MainScreen.kt` - 使用自定义输出目录生成报告，并显示完整路径
4. **修改** `README.md` - 更新使用文档，说明输出目录可配置功能

## 兼容性

- 完全向后兼容，原有的配置文件不受影响
- 默认行为保持不变，不影响现有用户使用习惯
