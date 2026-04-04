import json
import yaml  # type: ignore
import logging
from typing import Union, Dict, Any

from pysentinel.utils.exception import ScannerException

logger = logging.getLogger(__name__)


def load_config(config: Union[str, Dict]) -> Dict[str, Any]:
    """Load configuration from file or dict"""
    _config: Dict[str, Any] = {}
    try:
        if isinstance(config, str):
            with open(config, "r") as f:
                if config.endswith(".yaml") or config.endswith(".yml"):
                    loaded = yaml.safe_load(f)
                    if not isinstance(loaded, dict):
                        raise ScannerException(
                            "Invalid configuration: YAML file must contain a mapping, got "
                            f"{type(loaded).__name__}"
                        )
                    _config = loaded
                else:
                    _config = json.load(f)
        else:
            _config = config  # type: ignore[assignment]

        logger.info("Configuration loaded successfully")
        return _config

    except ScannerException:
        raise
    except Exception as e:
        raise ScannerException(f"Failed to load configuration: {e}")
