#!/usr/bin/env python3
"""
SuperPower 代码审查工具的主入口点。
处理完整的代码审查流程，包括：
1. SVN diff 收集和解析
2. 本地规则检查
3. 文件扫描和过滤
4. 用于全文审查的用户交互
5. AI 审查（如果已配置）
6. 报告生成
"""

import sys
import subprocess
import datetime
import tkinter as tk
from tkinter import messagebox
import logging

from src.diff_parser import DiffParser
from src.scanner import FileScanner
from src.local_rules import load_all_rules
from src.config import Config
from src.ai_reviewer import get_ai_client
from src.reporter import TextReporter, HTMLReporter, JSONReporter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"code_review_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主审查流程"""
    try:
        # 加载配置
        config = Config.load_from_env()

        # 步骤1: 获取SVN diff
        logger.info("步骤1: 收集SVN差异")
        try:
            diff_output = subprocess.check_output(["svn", "diff"], universal_newlines=True)
        except FileNotFoundError:
            logger.error("错误: 未找到SVN命令。请确保SVN已安装并在PATH中。")
            return 1
        except subprocess.CalledProcessError as e:
            logger.error(f"获取SVN差异时出错: {e}")
            return 1
        except Exception as e:
            logger.error(f"收集SVN差异时发生意外错误: {e}")
            return 1

        # 步骤2: 解析diff
        logger.info("步骤2: 解析SVN差异")
        parser = DiffParser(diff_output)
        file_diffs = parser.parse()
        logger.info(f"在差异中发现 {len(file_diffs)} 个修改的文件")

        # 步骤3: 扫描文件
        logger.info("步骤3: 扫描文件")
        scanner = FileScanner()
        try:
            scan_results = scanner.scan(file_diffs)
        except Exception as e:
            logger.error(f"文件扫描过程中出错: {e}")
            return 1

        # 步骤4: 在diff上运行本地规则
        logger.info("步骤4: 在差异上运行本地规则")
        rules = load_all_rules()
        findings = []

        for file_diff in scan_results["file_diffs"]:
            for rule in rules:
                try:
                    rule_findings = rule.check_diff(file_diff)
                    findings.extend(rule_findings)
                except Exception as e:
                    logger.error(f"对文件 {file_diff.file_path} 运行规则 {rule.__class__.__name__} 时出错: {e}")

        # 收集库变更通知
        findings.extend(scan_results["libs_notifications"])
        logger.info(f"在仅差异模式下发现 {len(findings)} 个问题")

        # 检查是否有BLOCK级别的问题
        has_block_issues = any(finding.severity == "BLOCK" for finding in findings)

        if has_block_issues:
            # 生成报告并阻止提交
            mode = "diff-only"
            meta = {
                "timestamp": datetime.datetime.now().isoformat(),
                "mode": mode,
                "file_count": len(file_diffs),
                "has_block_issues": True
            }
            generate_reports(findings, meta, config)
            logger.error("发现BLOCK级别的问题 - 提交被阻止")
            return 1

        # 步骤5: 询问用户是否进行全文审查
        logger.info("步骤5: 检查是否需要全文审查")
        mode = "diff-only"
        ai_client = None
        if config.has_ai_enabled():
            ai_client = get_ai_client(config)

        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口

            response = messagebox.askyesno(
                "代码审查",
                "Diff 审查通过，是否进行全文审查？[Yes/No]"
            )

            if response:
                mode = "diff-full"
                logger.info("开始全文审查")
                findings.extend(run_full_file_review(scan_results["file_diffs"], rules, ai_client))

        except Exception as e:
            logger.warning(f"无法显示GUI提示或处理全文审查: {e}")
            logger.info("继续仅差异审查")

        # 步骤6: 生成报告
        logger.info("步骤6: 生成报告")
        meta = {
            "timestamp": datetime.datetime.now().isoformat(),
            "mode": mode,
            "file_count": len(file_diffs),
            "has_block_issues": False
        }

        report_paths = generate_reports(findings, meta, config)
        logger.info("代码审查成功完成")
        logger.info(f"共发现 {len(findings)} 个问题")
        for path in report_paths:
            logger.info(f"报告已生成: {path}")

        return 0

    except Exception as e:
        logger.error(f"代码审查过程中的致命错误: {e}")
        return 1

def run_full_file_review(file_diffs, rules, ai_client):
    """对所有修改过的文件运行全文审查"""
    findings = []
    for file_diff in file_diffs:
        logger.debug(f"审查文件: {file_diff.file_path}")
        # 读取完整文件内容
        try:
            with open(file_diff.file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except FileNotFoundError:
            logger.warning(f"警告: 未找到文件 {file_diff.file_path}")
            continue
        except PermissionError:
            logger.warning(f"警告: 读取文件 {file_diff.file_path} 时权限被拒绝")
            continue
        except UnicodeDecodeError:
            logger.warning(f"警告: 读取文件 {file_diff.file_path} 时编码错误")
            continue
        except Exception as e:
            logger.warning(f"警告: 读取文件 {file_diff.file_path} 时出错: {e}")
            continue

        # 在完整文件上运行本地规则
        for rule in rules:
            try:
                rule_findings = rule.check_full_file(file_diff.file_path, file_content)
                findings.extend(rule_findings)
            except Exception as e:
                logger.error(f"在完整文件 {file_diff.file_path} 上运行规则 {rule.__class__.__name__} 时出错: {e}")

        # 如果已配置，运行AI审查
        if ai_client:
            try:
                logger.debug(f"对文件运行AI审查: {file_diff.file_path}")
                ai_findings = ai_client.review_code(file_diff.file_path, file_content)
                findings.extend(ai_findings)
            except Exception as e:
                logger.error(f"对文件 {file_diff.file_path} 进行AI审查时出错: {e}")

    logger.info(f"在全文审查中发现 {len(findings)} 个额外问题")
    return findings


def generate_reports(findings, meta, config):
    """使用所有可用的报告器生成报告"""
    reporters = [
        TextReporter(),
        HTMLReporter(),
        JSONReporter()
    ]

    report_paths = []
    for reporter in reporters:
        try:
            report_path = reporter.generate(findings, meta, config)
            report_paths.append(report_path)
        except Exception as e:
            logger.error(f"使用 {reporter.__class__.__name__} 生成报告时出错: {e}")

    return report_paths


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
