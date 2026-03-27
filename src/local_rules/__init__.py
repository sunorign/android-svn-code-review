import importlib
import pkgutil
import logging
from typing import List

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