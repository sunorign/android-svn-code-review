package com.codereview.gui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.codereview.core.ScanMode
import com.codereview.core.ScanSettings
import com.codereview.core.ScanSettingsLoader
import com.codereview.core.DiffGranularity
import com.codereview.core.AppSettings
import com.codereview.core.AppSettingsLoader
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File
import javax.swing.JFileChooser
import javax.swing.filechooser.FileSystemView

@Composable
fun ScanSettingsDialog(
    onDismiss: () -> Unit,
    onSaved: () -> Unit
) {
    var currentSettings by remember { mutableStateOf(ScanSettingsLoader.loadSettings()) }
    val appSettings = remember { AppSettingsLoader.loadSettings() }
    var currentOutputDirectory by remember { mutableStateOf(appSettings.outputDirectory) }
    var useDefaultOutput by remember { mutableStateOf(currentOutputDirectory.isNullOrBlank()) }
    var isSaving by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val coroutineScope = rememberCoroutineScope()

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("扫描设置") },
        text = {
            Column(
                modifier = Modifier
                    .width(500.dp)
                    .verticalScroll(rememberScrollState())
                    .padding(vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(20.dp)
            ) {
                // Scan Mode section
                Text("扫描模式:", style = MaterialTheme.typography.labelMedium)
                Column(
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    ScanMode.entries.forEach { mode ->
                        val displayName = when (mode) {
                            ScanMode.FULL -> "全局扫描 - 扫描所有代码文件"
                            ScanMode.SVN_DIFF -> "SVN Diff - 只检查 SVN 变更文件"
                            ScanMode.GIT_DIFF -> "Git Diff - 只检查 Git 变更文件"
                        }
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            RadioButton(
                                selected = currentSettings.scanMode == mode,
                                onClick = {
                                    currentSettings = currentSettings.copy(scanMode = mode)
                                }
                            )
                            Text(displayName)
                        }
                    }
                }

                // Diff Granularity section
                Text("Diff 检查粒度:", style = MaterialTheme.typography.labelMedium)
                Column(
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    DiffGranularity.entries.forEach { granularity ->
                        val displayName = when (granularity) {
                            DiffGranularity.WHOLE_FILE -> "检查整个变更文件（推荐）"
                            DiffGranularity.CHANGED_LINES -> "仅检查变更代码行"
                        }
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            RadioButton(
                                selected = currentSettings.diffGranularity == granularity,
                                onClick = {
                                    currentSettings = currentSettings.copy(diffGranularity = granularity)
                                },
                                enabled = currentSettings.scanMode != ScanMode.FULL
                            )
                            Text(displayName, color = MaterialTheme.colorScheme.onSurface.copy(
                                alpha = if (currentSettings.scanMode != ScanMode.FULL) 1f else 0.5f
                            ))
                        }
                    }
                }

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

                // Error message
                errorMessage?.let { error ->
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.errorContainer
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            error,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            modifier = Modifier.padding(12.dp)
                        )
                    }
                }
            }
        },
        confirmButton = {
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = {
                        errorMessage = null
                        isSaving = true
                        coroutineScope.launch(Dispatchers.IO) {
                            try {
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

                                launch(Dispatchers.Main) {
                                    isSaving = false
                                    onSaved()
                                }
                            } catch (e: Exception) {
                                launch(Dispatchers.Main) {
                                    errorMessage = "保存失败: ${e.message}"
                                    isSaving = false
                                }
                            }
                        }
                    },
                    enabled = !isSaving
                ) {
                    Text(if (isSaving) "保存中..." else "保存")
                }
            }
        },
        dismissButton = {
            OutlinedButton(onClick = onDismiss) {
                Text("取消")
            }
        }
    )
}
