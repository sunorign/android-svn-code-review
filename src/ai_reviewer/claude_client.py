from typing import List
import requests
import json
from .base_client import BaseAIClient, AIReviewResult, AIReviewFinding
from src.config import Config


class ClaudeClient(BaseAIClient):
    """Claude API客户端实现，用于AI代码审查。"""

    def __init__(self, config: Config):
        """
        初始化Claude API客户端。

        Args:
            config: 包含Anthropic API密钥的配置对象
        """
        self.config = config
        self.api_key = config.anthropic_api_key
        self.base_url = config.anthropic_api_url or "https://api.anthropic.com/v1/messages"
        self.default_model = config.anthropic_model or "claude-3-sonnet-20240229"
        self.max_tokens = config.anthropic_max_tokens or 4096
        self.timeout = config.api_timeout or 60
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

    def review_diff(self, file_path: str, diff_content: str, prompt_template: str) -> AIReviewResult:
        """
        使用Claude API审查代码差异块。

        Args:
            file_path: 正在审查的文件路径
            diff_content: 要审查的差异内容
            prompt_template: 包含占位符的提示模板

        Returns:
            包含审查结果或错误的AIReviewResult对象
        """
        return self._review_content(file_path, diff_content, prompt_template, "diff")

    def review_full_file(self, file_path: str, content: str, prompt_template: str) -> AIReviewResult:
        """
        使用Claude API审查完整文件。

        Args:
            file_path: 正在审查的文件路径
            content: 要审查的完整文件内容
            prompt_template: 包含占位符的提示模板

        Returns:
            包含审查结果或错误的AIReviewResult对象
        """
        return self._review_content(file_path, content, prompt_template, "full_file")

    def _review_content(self, file_path: str, content: str, prompt_template: str, review_type: str) -> AIReviewResult:
        """
        通用内容审查方法，处理代码差异和完整文件审查。

        Args:
            file_path: 正在审查的文件路径
            content: 要审查的内容（差异或完整文件）
            prompt_template: 包含占位符的提示模板
            review_type: 审查类型（"diff"表示差异，"full_file"表示完整文件）

        Returns:
            包含审查结果或错误的AIReviewResult对象
        """
        try:
            # 填充提示模板
            prompt = prompt_template.format(
                file_path=file_path,
                content=content
            )

            # 发起API调用
            response = self._make_api_call(prompt)

            # 解析响应
            if response["success"]:
                findings = self._parse_findings(response["data"], file_path)
                return AIReviewResult(
                    success=True,
                    findings=findings,
                    tokens_used=response.get("tokens_used", 0)
                )
            else:
                return AIReviewResult(
                    success=False,
                    findings=[],
                    error_message=response["error"]
                )

        except Exception as e:
            review_type_str = "diff" if review_type == "diff" else "full_file"
            return AIReviewResult(
                success=False,
                findings=[],
                error_message=f"Error reviewing {review_type_str} for {file_path}: {str(e)}"
            )

    def _make_api_call(self, prompt: str) -> dict:
        """
        调用Claude API。

        Args:
            prompt: 格式化后的提示文本

        Returns:
            包含成功状态、数据或错误信息的字典
        """
        try:
            # Claude API消息格式
            payload = {
                "model": self.default_model,
                "max_tokens": self.max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                # 从Claude响应中提取内容
                # Claude返回的内容格式为["content"][0]["text"]
                if "content" in data and len(data["content"]) > 0:
                    text_response = data["content"][0]["text"]

                    # 解析响应文本中的JSON
                    try:
                        # 查找JSON对象（处理可能的markdown包装）
                        if text_response.strip().startswith("```json"):
                            json_str = text_response.strip().split("```json")[1].split("```")[0].strip()
                        else:
                            json_str = text_response.strip()

                        parsed_data = json.loads(json_str)
                        return {
                            "success": True,
                            "data": parsed_data,
                            "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"解析JSON响应失败: {str(e)}, 原始响应: {text_response}"
                        }
                else:
                    return {
                        "success": False,
                        "error": "API响应中没有内容"
                    }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败，状态码: {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"API请求失败: {str(e)}"
            }

    def _parse_findings(self, data: dict, file_path: str) -> List[AIReviewFinding]:
        """
        解析API响应中的审查结果。

        Args:
            data: 解析后的JSON响应数据
            file_path: 审查结果对应的文件路径

        Returns:
            AIReviewFinding对象列表
        """
        findings = []

        if "findings" in data:
            for item in data["findings"]:
                # 确保所需字段存在
                if all(key in item for key in ["issue_type", "severity", "message"]):
                    finding = AIReviewFinding(
                        file_path=item.get("file_path", file_path),
                        line_start=item.get("line_start", 0),
                        line_end=item.get("line_end", 0),
                        issue_type=item["issue_type"],
                        severity=item["severity"],
                        message=item["message"],
                        suggestion=item.get("suggestion")
                    )
                    findings.append(finding)

        return findings
