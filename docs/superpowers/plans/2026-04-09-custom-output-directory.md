# 自定义输出目录功能 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 在 GUI 中增加自定义输出报告目录功能，用户可以选择保存报告的目录，设置持久化保存，重启后自动恢复。

**架构：** 新增 `AppSettings` 数据类和 `AppSettingsLoader` 加载器，配置文件保存到 `~/.code-review/app_settings.json`，在 `ScanSettingsDialog` 对话框中添加输出目录选择 UI，修改 `MainScreen` 使用自定义目录生成报告并在结果中显示完整路径。

**技术栈：** Kotlin + Compose Multiplatform + Kotlinx Serialization

---

## 文件修改清单

| 文件 | 操作 | 职责 |
|------|------|------|
| `src/main/kotlin/com/codereview/core/AppSettings.kt` | **新建** | AppSettings 数据类 + AppSettingsLoader 加载器 |
| `src/main/kotlin/com/codereview/gui/ScanSettingsDialog.kt` | **修改** | 添加输出目录选择 UI，包括文本框、浏览按钮、使用默认复选框，添加目录验证 |
| `src/main/kotlin/com/codereview/gui/MainScreen.kt` | **修改** | 加载 AppSettings，使用自定义输出目录，结果中显示完整路径 |
| `README.md` | **修改** | 更新文档，说明输出目录可配置功能 |

---

### 任务 1：新建 AppSettings.kt

**文件：**
- 创建：`src/main/kotlin/com/codereview/core/AppSettings.kt`

- [ ] **步骤 1：新建文件编写完整代码**

```kotlin
package com.codereview.core

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File

@Serializable
data class AppSettings(
    val outputDirectory: String? = null
)

object AppSettingsLoader {

    private val json = Json { prettyPrint = true }

    fun loadSettings(): AppSettings {
        val userConfigFile = getUserConfigFile()
        return if (userConfigFile.exists()) {
            val jsonText = userConfigFile.readText()
            json.decodeFromString<AppSettings>(jsonText)
        } else {
            AppSettings()
        }
    }

    fun saveSettings(settings: AppSettings) {
        val userConfigFile = getUserConfigFile()
        val configDir = userConfigFile.parentFile
        if (!configDir.exists()) {
            configDir.mkdirs()
        }
        val jsonText = json.encodeToString(AppSettings.serializer(), settings)
        userConfigFile.writeText(jsonText)
    }

    fun getUserConfigFile(): File {
        val homeDir = System.getProperty("user.home")
        return File(homeDir, ".code-review/app_settings.json")
    }

    /**
     * Get the effective output directory to use.
     * Returns user configured directory if set and valid, otherwise defaults to ~/code-review-output
     */
    fun getEffectiveOutputDirectory(settings: AppSettings): File {
        val configured = settings.outputDirectory
        if (!configured.isNullOrBlank()) {
            return File(configured)
        }
        val homeDir = System.getProperty("user.home")
        return File(homeDir, "code-review-output")
    }
}
```

- [ ] **步骤 2：Commit**

```bash
git add src/main/kotlin/com/codereview/core/AppSettings.kt
git commit -m "feat: add AppSettings with AppSettingsLoader for custom output directory"
```

---

### 任务 2：修改 ScanSettingsDialog 添加输出目录选择 UI

**文件：**
- 修改：`src/main/kotlin/com/codereview/gui/ScanSettingsDialog.kt`

- [ ] **步骤 1：添加 import 和状态变量**

在文件开头添加 import：

```kotlin
import com.codereview.core.AppSettings
import com.codereview.core.AppSettingsLoader
import java.io.File
import javax.swing.JFileChooser
import javax.swing.filechooser.FileSystemView
```

在函数内部添加状态变量（在 `var currentSettings by remember...` 之后添加）：

```kotlin
val appSettings = remember { AppSettingsLoader.loadSettings() }
var currentOutputDirectory by remember { mutableStateOf(appSettings.outputDirectory) }
var useDefaultOutput by remember { mutableStateOf(currentOutputDirectory.value.isNullOrBlank()) }
```

- [ ] **步骤 2：在 Diff 粒度区域之后添加输出目录选择 UI**

在 Diff 粒度区域 `}` 之后，错误消息之前添加：

```kotlin
// Output Directory section
Text("输出目录:", style = MaterialTheme.typography.labelMedium)
Column(
    verticalArrangement = Arrangement.spacedBy(4.dp)
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier.fillMaxWidth()
    ) {
        Checkbox(
            checked = useDefaultOutput,
            onCheckedChange = { checked ->
                useDefaultOutput = checked
            }
        )
        Text("使用默认路径 (~/code-review-output)")
    }

    if (!useDefaultOutput) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            OutlinedTextField(
                value = currentOutputDirectory ?: "",
                onValueChange = { /* read-only */ },
                modifier = Modifier.weight(1f),
                placeholder = { Text("点击右侧按钮选择目录") },
                singleLine = true,
                enabled = false
            )
            Spacer(modifier = Modifier.width(8.dp))
            Button(onClick = {
                val chooser = JFileChooser(FileSystemView.getFileSystemView().homeDirectory)
                chooser.fileSelectionMode = JFileChooser.DIRECTORIES_ONLY
                chooser.dialogTitle = "选择输出目录"
                val result = chooser.showOpenDialog(null)
                if (result == JFileChooser.APPROVE_OPTION) {
                    currentOutputDirectory = chooser.selectedFile.absolutePath
                }
            }) {
                Text("浏览...")
            }
        }
    }
}
```

- [ ] **步骤 3：修改保存逻辑，添加目录验证**

在保存代码处，try 块内部修改：

```kotlin
// Validate output directory before saving
if (!useDefaultOutput) {
    val dirPath = currentOutputDirectory
    if (dirPath.isNullOrBlank()) {
        errorMessage = "请选择输出目录，或勾选'使用默认路径'"
        isSaving = false
        return@launch
    }
    val dir = File(dirPath)
    if (!dir.isAbsolute) {
        errorMessage = "请选择绝对路径: $dirPath"
        isSaving = false
        return@launch
    }
    if (!dir.exists()) {
        // Try to create directory if it doesn't exist
        if (!dir.mkdirs()) {
            errorMessage = "无法创建目录: $dirPath，请检查权限"
            isSaving = false
            return@launch
        }
    }
    if (!dir.canWrite()) {
        errorMessage = "目录无写权限: $dirPath，请选择其他目录"
        isSaving = false
        return@launch
    }
}

// Save scan settings
ScanSettingsLoader.saveSettings(currentSettings)

// Save app settings
val newAppSettings = AppSettings(
    outputDirectory = if (useDefaultOutput) null else currentOutputDirectory
)
AppSettingsLoader.saveSettings(newAppSettings)
```

- [ ] **步骤 4：重新整理编译单元，确保括号匹配**

检查代码结构，确保所有 `{}` 正确闭合，变量作用域正确。

- [ ] **步骤 5：编译验证，修复语法错误**

运行：`./gradlew.bat compileKotlin`
预期：编译成功。如果有错误，修复后重新编译。

- [ ] **步骤 6：Commit**

```bash
git add src/main/kotlin/com/codereview/gui/ScanSettingsDialog.kt
git commit -m "feat: add output directory selection UI to ScanSettingsDialog"
```

---

### 任务 3：修改 MainScreen 使用自定义输出目录

**文件：**
- 修改：`src/main/kotlin/com/codereview/gui/MainScreen.kt`

- [ ] **步骤 1：添加 import**

在文件开头添加 import：

```kotlin
import com.codereview.core.AppSettingsLoader
```

- [ ] **步骤 2：修改 runReview 函数中的输出目录获取**

找到：

```kotlin
val outputDir = File(System.getProperty("user.home"), "code-review-output")
outputDir.mkdirs()
```

替换为：

```kotlin
val appSettings = AppSettingsLoader.loadSettings()
val outputDir = AppSettingsLoader.getEffectiveOutputDirectory(appSettings)
outputDir.mkdirs()
```

- [ ] **步骤 3：修改结果文本，显示实际输出目录路径**

找到：

```kotlin
resultText = "审查完成，共扫描 ${result.scannedFiles} 个文件，发现 ${result.localFindings.size} 个本地问题，${result.aiFindings.size} 个AI问题\n"
resultText += "报告已保存到输出目录\n"
```

替换为：

```kotlin
resultText = "审查完成，共扫描 ${result.scannedFiles} 个文件，发现 ${result.localFindings.size} 个本地问题，${result.aiFindings.size} 个AI问题\n"
resultText += "报告已保存到目录:\n$outputDir\n"
```

- [ ] **步骤 4：更新 getOutputFile 函数默认值**

找到 `getOutputFile` 函数：

```kotlin
private fun getOutputFile(
    timestamp: String,
    extension: String,
    outputDir: String = System.getProperty("user.home") + "/code-review-output"
): File
```

将默认参数修改为使用 `AppSettingsLoader`：

```kotlin
private fun getOutputFile(
    timestamp: String,
    extension: String,
    outputDir: String = AppSettingsLoader.getEffectiveOutputDirectory(AppSettingsLoader.loadSettings()).absolutePath
): File
```

- [ ] **步骤 5：编译验证**

运行：`./gradlew.bat compileKotlin`
预期：编译成功。

- [ ] **步骤 6：Commit**

```bash
git add src/main/kotlin/com/codereview/gui/MainScreen.kt
git commit -m "feat: use custom output directory in MainScreen and show path in result"
```

---

### 任务 4：更新 README.md 文档

**文件：**
- 修改：`README.md`

- [ ] **步骤 1：在 GUI 使用说明中添加输出目录说明**

在"**扫描设置说明**："部分之后添加：

```
- **输出目录**：可自定义报告保存目录，默认 `~/code-review-output`，勾选"使用默认路径"或自定义选择
```

- [ ] **步骤 2：在最近更新部分添加此项功能**

在 v2.0 更新列表中添加：

```
- ✅ **支持自定义输出目录**：GUI 中可选择报告保存目录，设置持久化保存
```

- [ ] **步骤 3：Commit**

```bash
git add README.md
git commit -m "docs: update README for custom output directory feature"
```

---

## 验收标准

功能完成后应满足：

1. ✅ 首次启动默认使用 `~/code-review-output`
2. ✅ 用户可在"扫描设置"中取消勾选"使用默认路径"，通过浏览按钮选择自定义目录
3. ✅ 保存时验证目录存在且可写，验证失败显示错误消息
4. ✅ 重启应用后，用户选择的目录自动恢复
5. ✅ 勾选"使用默认路径"恢复为默认目录
6. ✅ 审查完成后，结果文本中显示完整输出目录路径
7. ✅ 编译通过，可正常运行 GUI
