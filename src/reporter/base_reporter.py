import os
import datetime
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseReporter(ABC):
    """Base abstract class for all reporters."""

    def __init__(self, output_dir: str = "code-review-output"):
        """Initialize reporter with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _get_timestamp(self, meta: Dict[str, Any]) -> datetime.datetime:
        """Get timestamp from meta or use current time."""
        timestamp = meta.get('timestamp', datetime.datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.fromisoformat(timestamp)
        return timestamp

    def _format_timestamp(self, timestamp: Optional[datetime.datetime] = None) -> str:
        """Format timestamp for filename."""
        if timestamp is None:
            timestamp = datetime.datetime.now()
        return timestamp.strftime('%Y%m%d-%H%M%S')

    @abstractmethod
    def generate_report(self,
                       local_findings: List[Any],
                       ai_findings: List[Any],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """Abstract method to generate report content."""
        pass

    def generate(self, findings: List[Any], meta: Dict[str, Any], config=None) -> str:
        """Generate report from all findings (local and AI) and write to file."""
        # Separate local and AI findings
        local_findings = []
        ai_findings = []

        for finding in findings:
            # Check type of finding to separate them
            if hasattr(finding, 'rule_name'):
                local_findings.append(finding)
            elif hasattr(finding, 'issue_type'):
                ai_findings.append(finding)
            else:
                # For libs notifications and other findings
                local_findings.append(finding)

        return self.write_report(local_findings, ai_findings, meta)

    def write_report(self,
                    local_findings: List[Any],
                    ai_findings: List[Any],
                    meta: Dict[str, Any],
                    libs_reminder: str = "") -> str:
        """Generate and write report to output file."""
        content = self.generate_report(local_findings, ai_findings, meta, libs_reminder)

        timestamp = self._get_timestamp(meta)
        filename = f"review-result-{self._format_timestamp(timestamp)}.{self._get_file_extension()}"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    @abstractmethod
    def _get_file_extension(self) -> str:
        """Abstract method to get file extension for report format."""
        pass