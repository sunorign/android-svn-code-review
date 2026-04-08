package com.codereview.gui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.Checkbox
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.codereview.rules.LocalRuleSettings
import com.codereview.rules.LocalRuleSettingsLoader
import com.codereview.rules.RuleState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun LocalRulesSettingsDialog(
    onDismiss: () -> Unit,
    onSaved: () -> Unit
) {
    val currentSettings = remember { LocalRuleSettingsLoader.loadSettings() }
    var localEnabled by remember { mutableStateOf(currentSettings.localEnabled) }
    val ruleStates = remember {
        mutableStateMapOf<String, RuleState>().apply {
            currentSettings.rules.forEach { rule ->
                this[rule.className] = rule.copy()
            }
        }
    }
    val expandedGroups = remember {
        mutableStateMapOf<String, Boolean>().apply {
            // All groups expanded by default
            ruleStates.values.map { it.groupName }.distinct().forEach { group ->
                this[group] = true
            }
        }
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("本地规则设置") },
        text = {
            Column(
                modifier = Modifier
                    .width(600.dp)
                    .verticalScroll(rememberScrollState())
                    .padding(vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Master toggle for local review
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Checkbox(
                        checked = localEnabled,
                        onCheckedChange = { localEnabled = it }
                    )
                    Text("启用本地规则审查", style = MaterialTheme.typography.bodyLarge)
                }

                // Rules grouped by groupName
                Column(
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    val groupedRules = ruleStates.values.groupBy { it.groupName }
                    groupedRules.forEach { (groupName, rules) ->
                        val expanded = expandedGroups[groupName] ?: true
                        val enabledCount = rules.count { it.enabled }
                        val totalCount = rules.size

                        // Group header with expand/collapse
                        Card(
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clickable {
                                            expandedGroups[groupName] = !expanded
                                        }
                                        .padding(12.dp)
                                ) {
                                    Text(
                                        "$groupName ($enabledCount/$totalCount 启用)",
                                        style = MaterialTheme.typography.titleMedium,
                                        modifier = Modifier.weight(1f)
                                    )
                                    Text(
                                        if (expanded) "▼" else "▶",
                                        style = MaterialTheme.typography.titleMedium
                                    )
                                }

                                if (expanded) {
                                    Column(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(start = 12.dp, end = 12.dp, bottom = 12.dp),
                                        verticalArrangement = Arrangement.spacedBy(4.dp)
                                    ) {
                                        rules.sortedBy { it.displayName }.forEach { rule ->
                                            Row(
                                                verticalAlignment = Alignment.CenterVertically,
                                                modifier = Modifier.fillMaxWidth()
                                            ) {
                                                Checkbox(
                                                    checked = rule.enabled,
                                                    enabled = localEnabled,
                                                    onCheckedChange = { checked ->
                                                        ruleStates[rule.className] = rule.copy(enabled = checked)
                                                    }
                                                )
                                                Column(
                                                    modifier = Modifier.weight(1f)
                                                ) {
                                                    Text(
                                                        rule.displayName,
                                                        style = MaterialTheme.typography.bodyLarge
                                                    )
                                                    Text(
                                                        rule.description,
                                                        style = MaterialTheme.typography.bodySmall,
                                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                                    )
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        confirmButton = {
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                TextButton(onClick = onDismiss) {
                    Text("取消")
                }
                TextButton(onClick = {
                    val updatedSettings = LocalRuleSettings(
                        localEnabled = localEnabled,
                        rules = ruleStates.values.toList()
                    )
                    LocalRuleSettingsLoader.saveSettings(updatedSettings)
                    onSaved()
                    onDismiss()
                }) {
                    Text("保存")
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("取消")
            }
        }
    )
}
