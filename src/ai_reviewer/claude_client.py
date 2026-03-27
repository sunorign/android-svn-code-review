from typing import List
import requests
import json
from .base_client import BaseAIClient, AIReviewResult, AIReviewFinding
from src.config import Config


class ClaudeClient(BaseAIClient):
    """Claude API client implementation for AI review."""

    def __init__(self, config: Config):
        """
        Initialize the Claude API client.

        Args:
            config: Configuration object containing Anthropic API key
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
        Review a diff chunk using Claude API.

        Args:
            file_path: Path to the file being reviewed
            diff_content: Diff content to review
            prompt_template: Prompt template with placeholders

        Returns:
            AIReviewResult containing findings or error
        """
        return self._review_content(file_path, diff_content, prompt_template, "diff")

    def review_full_file(self, file_path: str, content: str, prompt_template: str) -> AIReviewResult:
        """
        Review a full file using Claude API.

        Args:
            file_path: Path to the file being reviewed
            content: Full file content to review
            prompt_template: Prompt template with placeholders

        Returns:
            AIReviewResult containing findings or error
        """
        return self._review_content(file_path, content, prompt_template, "full_file")

    def _review_content(self, file_path: str, content: str, prompt_template: str, review_type: str) -> AIReviewResult:
        """
        Generic content review method to handle both diff and full file reviews.

        Args:
            file_path: Path to the file being reviewed
            content: Content to review (diff or full file)
            prompt_template: Prompt template with placeholders
            review_type: Type of review ("diff" or "full_file")

        Returns:
            AIReviewResult containing findings or error
        """
        try:
            # Fill prompt template with content
            prompt = prompt_template.format(
                file_path=file_path,
                content=content
            )

            # Make API call
            response = self._make_api_call(prompt)

            # Parse response
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
            review_type_str = "diff" if review_type == "diff" else "file"
            return AIReviewResult(
                success=False,
                findings=[],
                error_message=f"Error reviewing {review_type_str} for {file_path}: {str(e)}"
            )

    def _make_api_call(self, prompt: str) -> dict:
        """
        Make an API call to Claude API.

        Args:
            prompt: Formatted prompt to send

        Returns:
            Dictionary with success status, data or error
        """
        try:
            # Claude API message format
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
                # Extract content from Claude's response
                # Claude returns content in ["content"][0]["text"]
                if "content" in data and len(data["content"]) > 0:
                    text_response = data["content"][0]["text"]

                    # Parse JSON from response text
                    try:
                        # Find JSON object in response (handle possible markdown wrapping)
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
                            "error": f"Failed to parse JSON response: {str(e)}, Raw response: {text_response}"
                        }
                else:
                    return {
                        "success": False,
                        "error": "No content in API response"
                    }
            else:
                return {
                    "success": False,
                    "error": f"API call failed with status {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }

    def _parse_findings(self, data: dict, file_path: str) -> List[AIReviewFinding]:
        """
        Parse findings from API response.

        Args:
            data: Parsed JSON response data
            file_path: File path for findings

        Returns:
            List of AIReviewFinding objects
        """
        findings = []

        if "findings" in data:
            for item in data["findings"]:
                # Ensure required fields are present
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
