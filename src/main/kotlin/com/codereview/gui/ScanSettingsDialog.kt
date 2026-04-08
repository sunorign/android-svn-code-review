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
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Composable
fun ScanSettingsDialog(
    onDismiss: () -> Unit,
    onSaved: () -> Unit
) {
    var currentSettings by remember { mutableStateOf(ScanSettingsLoader.loadSettings()) }
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
                                ScanSettingsLoader.saveSettings(currentSettings)
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