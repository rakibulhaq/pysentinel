import json
import yaml
import logging
from typing import Union, Dict

from pysentinel.utils.exception import ScannerException

logger = logging.getLogger(__name__)


def load_config(config: Union[str, Dict]):
    """Load configuration from file or dict"""
    _config = None
    try:
        if isinstance(config, str):
            with open(config, 'r') as f:
                if config.endswith('.yaml') or config.endswith('.yml'):
                    _config = yaml.safe_load(f)
                else:
                    _config = json.load(f)
        else:
            _config = config

        logger.info("Configuration loaded successfully")
        return _config

    except Exception as e:
        raise ScannerException(f"Failed to load configuration: {e}")
