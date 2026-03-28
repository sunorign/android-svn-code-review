from typing import List
import requests
import json
from .base_client import BaseAIClient, AIReviewResult, AIReviewFinding
from src.config import Config


class OpenRouterClient(BaseAIClient):
    """OpenRouter API客户端实现，用于AI代码审查。"""

    def __init__(self, config: Config):
        """
        初始化OpenRouter客户端。

        参数:
            config: 包含OpenRouter API密钥的配置对象
        """
        self.config = config
        self.api_key = config.openrouter_api_key
        self.base_url = config.openrouter_api_url or "https://openrouter.ai/api/v1/chat/completions"
        self.default_model = config.openrouter_model or "anthropic/claude-3-sonnet"
        self.max_tokens = config.openrouter_max_tokens or 4096
        self.timeout = config.api_timeout or 60
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": config.openrouter_http_referer or "",
            "Content-Type": "application/json"
        }

    def review_diff(self, file_path: str, diff_content: str, prompt_template: str) -> AIReviewResult:
        """
        使用OpenRouter API审查代码差异块。

        Args:
            file_path: 被审查文件的路径
            diff_content: 要审查的代码差异内容
            prompt_template: 带有占位符的提示模板

        Returns:
            包含审查结果或错误的AIReviewResult对象
        """
        return self._review_content(file_path, diff_content, prompt_template, "diff")

    def review_full_file(self, file_path: str, content: str, prompt_template: str) -> AIReviewResult:
        """
        使用OpenRouter API审查完整文件。

        Args:
            file_path: 被审查文件的路径
            content: 要审查的完整文件内容
            prompt_template: 带有占位符的提示模板

        Returns:
            包含审查结果或错误的AIReviewResult对象
        """
        return self._review_content(file_path, content, prompt_template, "full_file")

    def _review_content(self, file_path: str, content: str, prompt_template: str, review_type: str) -> AIReviewResult:
        """
        通用内容审查方法，处理代码差异和完整文件审查。

        Args:
            file_path: 被审查文件的路径
            content: 要审查的内容（代码差异或完整文件）
            prompt_template: 带有占位符的提示模板
            review_type: 审查类型（"diff"表示代码差异，"full_file"表示完整文件）

        Returns:
            包含审查结果或错误的AIReviewResult对象
        """
        try:
            # 填充提示模板内容
            prompt = prompt_template.format(
                file_path=file_path,
                content=content
            )

            # 调用API
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
            review_type_str = "代码差异" if review_type == "diff" else "文件"
            return AIReviewResult(
                success=False,
                findings=[],
                error_message=f"审查{review_type_str} {file_path}时出错: {str(e)}"
            )

    def _make_api_call(self, prompt: str) -> dict:
        """
        调用OpenRouter API。

        Args:
            prompt: 格式化后的提示内容

        Returns:
            包含成功状态、数据或错误信息的字典
        """
        try:
            # OpenRouter API消息格式（与OpenAI聊天完成格式相同）
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
                # 从OpenRouter响应中提取内容
                if "choices" in data and len(data["choices"]) > 0:
                    text_response = data["choices"][0]["message"]["content"]

                    # 解析响应文本中的JSON
                    try:
                        # 找到响应中的JSON对象（处理可能的markdown包装）
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
                        "error": "API响应中没有选项"
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
        从API响应中解析审查结果。

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
