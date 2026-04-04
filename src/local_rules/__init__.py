import importlib
import pkgutil
import logging
from typing import List, Tuple, Optional

from src.local_rules.base_rule import BaseRule

logger = logging.getLogger(__name__)


def load_all_rules() -> List[BaseRule]:
    """Dynamically load all rule classes from all submodules."""
    rules: List[BaseRule] = []

    # Find all subpackages under local_rules
    import src.local_rules
    for _, package_name, is_pkg in pkgutil.iter_modules(src.local_rules.__path__):
        if not is_pkg:
            continue

        try:
            # Import the package
            pkg = importlib.import_module(f"src.local_rules.{package_name}")

            # Load all modules from this package
            for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
                try:
                    module = importlib.import_module(f"{pkg.__name__}.{module_name}")

                    # Look for all BaseRule subclasses in the module
                    for attr_name in dir(module):
                        try:
                            attr = getattr(module, attr_name)
                            if isinstance(attr, type) and issubclass(attr, BaseRule) and attr != BaseRule:
                                rules.append(attr())
                        except Exception as e:
                            logger.warning(f"Failed to process attribute {attr_name} in module {module.__name__}: {e}")
                            continue

                except Exception as e:
                    logger.warning(f"Failed to load module {package_name}.{module_name}: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Failed to load package {package_name}: {e}")
            continue

    return rules


def list_available_projects() -> List[Tuple[str, str]]:
    """List all available projects for GUI dropdown.

    Returns:
        List of (project_key, display_name) tuples.
    """
    projects: List[Tuple[str, str]] = []

    import src.local_rules.pos_project_rules as pos_package
    for _, project_key, is_pkg in pkgutil.iter_modules(pos_package.__path__):
        if not is_pkg:
            continue
        try:
            project_module = importlib.import_module(f"src.local_rules.pos_project_rules.{project_key}")
            if hasattr(project_module, "PROJECT_DISPLAY_NAME"):
                display_name = project_module.PROJECT_DISPLAY_NAME
                projects.append((project_key, display_name))
        except Exception as e:
            logger.warning(f"Failed to load project {project_key}: {e}")
            continue

    return projects


def load_project_rules(project_key: str) -> List[BaseRule]:
    """Load rules for specific project.

    Args:
        project_key: project directory name in pos_project_rules.

    Returns:
        List of enabled rules for this project as configured in the project's __init__.py.
    """
    try:
        module = importlib.import_module(f"src.local_rules.pos_project_rules.{project_key}")
        if hasattr(module, "ENABLED_RULES"):
            return module.ENABLED_RULES
        else:
            logger.warning(f"Project {project_key} has no ENABLED_RULES config, returning empty list")
            return []
    except Exception as e:
        logger.error(f"Failed to load project rules for {project_key}: {e}")
        return []
