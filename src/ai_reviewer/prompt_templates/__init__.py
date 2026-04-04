"""AI提示词加载模块 - 按项目加载提示词

自动识别项目配置的提示词，找不到时兜底使用通用提示词
"""
import os
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def get_project_prompts(project_key: Optional[str] = None) -> Tuple[str, str]:
    """Get the prompt template paths (without extension) for given project.

    Args:
        project_key: project key (directory name under pos_projects),
                     None for default prompts.

    Returns:
        (diff_template_name, full_template_name) -> both are full paths relative to
                 this prompt_templates directory, without .md extension.
        If project has multiple matches, last matching wins.
        If not found, fall back to default.
    """
    diff_name = None
    full_name = None

    if project_key:
        try:
            # 导入项目配置模块
            import importlib
            module = importlib.import_module(f"src.ai_reviewer.prompt_templates.pos_projects.{project_key}")
            if hasattr(module, "ENABLED_PROMPTS"):
                enabled_prompts = module.ENABLED_PROMPTS
                # iterate from last to first, last matching wins
                for prompt_file in reversed(enabled_prompts):
                    base_name = prompt_file.rsplit('.', 1)[0]  # remove .md
                    lower_name = prompt_file.lower()
                    # full 权重更高，先处理 diff，full 会覆盖 diff 如果文件名同时包含
                    if 'diff' in lower_name and diff_name is None:
                        diff_name = f"pos_projects/{project_key}/{base_name}"
                    if 'full' in lower_name:
                        full_name = f"pos_projects/{project_key}/{base_name}"
                        if 'diff' in lower_name:
                            diff_name = None  # full 权重更高，覆盖 diff
        except Exception as e:
            logger.warning(f"Failed to load prompts for project {project_key}: {e}")

    # 兜底：没找到用默认
    if diff_name is None:
        diff_name = "common/diff-review"
    if full_name is None:
        full_name = "common/full-review"

    return diff_name, full_name


def load_prompt_content(template_name: str) -> str:
    """Load prompt template content from file by name.

    Args:
        template_name: template name like "common/diff-review" or "pos_projects/payment/xxx"

    Returns:
        Full content of the template file.
    """
    # 构建完整路径相对于 src/ai_reviewer/prompt_templates/
    full_path = os.path.join(
        os.path.dirname(__file__),
        template_name + ".md"
    )
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()
