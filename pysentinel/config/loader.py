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
                    _config = yaml.safe_load(f)  # type: ignore[assignment]
                else:
                    _config = json.load(f)
        else:
            _config = config  # type: ignore[assignment]

        logger.info("Configuration loaded successfully")
        return _config

    except Exception as e:
        raise ScannerException(f"Failed to load configuration: {e}")
