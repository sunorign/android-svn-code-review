#!/usr/bin/env python3
"""
Main entry point for the SuperPower Code Review tool.
Handles the complete code review process including:
1. SVN diff collection and parsing
2. Local rule checking
3. File scanning and filtering
4. User interaction for full-file review
5. AI review (if configured)
6. Report generation
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

# Configure logging
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
    """Main review process"""
    try:
        # Load configuration
        config = Config.load_from_env()

        # Step 1: Get SVN diff
        logger.info("Step 1: Collecting SVN diff")
        try:
            diff_output = subprocess.check_output(["svn", "diff"], universal_newlines=True)
        except FileNotFoundError:
            logger.error("Error: SVN command not found. Make sure SVN is installed and in PATH.")
            return 1
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting SVN diff: {e}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error while collecting SVN diff: {e}")
            return 1

        # Step 2: Parse diff
        logger.info("Step 2: Parsing SVN diff")
        parser = DiffParser(diff_output)
        file_diffs = parser.parse()
        logger.info(f"Found {len(file_diffs)} modified files in diff")

        # Step 3: Scan files
        logger.info("Step 3: Scanning files")
        scanner = FileScanner()
        try:
            scan_results = scanner.scan(file_diffs)
        except Exception as e:
            logger.error(f"Error during file scanning: {e}")
            return 1

        # Step 4: Run local rules on diff
        logger.info("Step 4: Running local rules on diff")
        rules = load_all_rules()
        findings = []

        for file_diff in scan_results["file_diffs"]:
            for rule in rules:
                try:
                    rule_findings = rule.check_diff(file_diff)
                    findings.extend(rule_findings)
                except Exception as e:
                    logger.error(f"Error running rule {rule.__class__.__name__} on file {file_diff.file_path}: {e}")

        # Collect libs change notifications
        findings.extend(scan_results["libs_notifications"])
        logger.info(f"Found {len(findings)} issues in diff-only mode")

        # Check for BLOCK level issues
        has_block_issues = any(finding.severity == "BLOCK" for finding in findings)

        if has_block_issues:
            # Generate reports and block commit
            mode = "diff-only"
            meta = {
                "timestamp": datetime.datetime.now().isoformat(),
                "mode": mode,
                "file_count": len(file_diffs),
                "has_block_issues": True
            }
            generate_reports(findings, meta, config)
            logger.error("BLOCK level issues found - commit blocked")
            return 1

        # Step 5: Ask user for full file review
        logger.info("Step 5: Checking if full file review is requested")
        mode = "diff-only"
        ai_client = None
        if config.has_ai_enabled():
            ai_client = get_ai_client(config)

        try:
            root = tk.Tk()
            root.withdraw()  # Hide main window

            response = messagebox.askyesno(
                "Code Review",
                "Diff 审查通过，是否进行全文审查？[Yes/No]"
            )

            if response:
                mode = "diff-full"
                logger.info("Starting full file review")
                findings.extend(run_full_file_review(scan_results["file_diffs"], rules, ai_client))

        except Exception as e:
            logger.warning(f"Unable to display GUI prompt or process full file review: {e}")
            logger.info("Continuing with diff-only review")

        # Step 6: Generate reports
        logger.info("Step 6: Generating reports")
        meta = {
            "timestamp": datetime.datetime.now().isoformat(),
            "mode": mode,
            "file_count": len(file_diffs),
            "has_block_issues": False
        }

        report_paths = generate_reports(findings, meta, config)
        logger.info("Code review completed successfully")
        logger.info(f"Total {len(findings)} issues found")
        for path in report_paths:
            logger.info(f"Report generated: {path}")

        return 0

    except Exception as e:
        logger.error(f"Fatal error in code review process: {e}")
        return 1

def run_full_file_review(file_diffs, rules, ai_client):
    """Run full file review for all modified files"""
    findings = []
    for file_diff in file_diffs:
        logger.debug(f"Reviewing file: {file_diff.file_path}")
        # Read full file content
        try:
            with open(file_diff.file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except FileNotFoundError:
            logger.warning(f"Warning: File {file_diff.file_path} not found")
            continue
        except PermissionError:
            logger.warning(f"Warning: Permission denied when reading file {file_diff.file_path}")
            continue
        except UnicodeDecodeError:
            logger.warning(f"Warning: Encoding error when reading file {file_diff.file_path}")
            continue
        except Exception as e:
            logger.warning(f"Warning: Error reading file {file_diff.file_path}: {e}")
            continue

        # Run local rules on full file
        for rule in rules:
            try:
                rule_findings = rule.check_full_file(file_diff.file_path, file_content)
                findings.extend(rule_findings)
            except Exception as e:
                logger.error(f"Error running rule {rule.__class__.__name__} on full file {file_diff.file_path}: {e}")

        # Run AI review if configured
        if ai_client:
            try:
                logger.debug(f"Running AI review on file: {file_diff.file_path}")
                ai_findings = ai_client.review_code(file_diff.file_path, file_content)
                findings.extend(ai_findings)
            except Exception as e:
                logger.error(f"Error during AI review of file {file_diff.file_path}: {e}")

    logger.info(f"Found {len(findings)} additional issues in full file review")
    return findings


def generate_reports(findings, meta, config):
    """Generate reports using all available reporters"""
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
            logger.error(f"Error generating report with {reporter.__class__.__name__}: {e}")

    return report_paths


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
