import os
import datetime
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from src.reporter.unified_finding import UnifiedFinding
from src.reporter.unified_finding_processor import UnifiedFindingProcessor


class BaseReporter(ABC):
    """所有报告生成器的基础抽象类。"""

    def __init__(self, output_dir: str = "code-review-output"):
        """使用输出目录初始化报告生成器。"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.processor = UnifiedFindingProcessor()

    def _get_timestamp(self, meta: Dict[str, Any]) -> datetime.datetime:
        """从元数据获取时间戳，或使用当前时间。"""
        timestamp = meta.get('timestamp', datetime.datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.fromisoformat(timestamp)
        return timestamp

    def _format_timestamp(self, timestamp: Optional[datetime.datetime] = None) -> str:
        """为文件名格式化时间戳。"""
        if timestamp is None:
            timestamp = datetime.datetime.now()
        return timestamp.strftime('%Y%m%d-%H%M%S')

    @abstractmethod
    def generate_report(self,
                       findings: List[UnifiedFinding],
                       meta: Dict[str, Any],
                       libs_reminder: str = "") -> str:
        """生成报告内容的抽象方法。"""
        pass

    def generate(self,
                local_findings: List[Any],
                ai_findings: List[Any],
                meta: Dict[str, Any],
                config=None) -> str:
        """从所有发现（本地和AI）生成报告并写入文件。"""

        # 转换为统一格式
        findings = self.processor.process_all(local_findings, ai_findings)

        return self.write_report(findings, meta)

    def write_report(self,
                    findings: List[UnifiedFinding],
                    meta: Dict[str, Any],
                    libs_reminder: str = "") -> str:
        """生成报告并写入输出文件。"""
        content = self.generate_report(findings, meta, libs_reminder)

        timestamp = self._get_timestamp(meta)
        filename = f"review-result-{self._format_timestamp(timestamp)}.{self._get_file_extension()}"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    @abstractmethod
    def _get_file_extension(self) -> str:
        """获取报告格式文件扩展名的抽象方法。"""
        pass