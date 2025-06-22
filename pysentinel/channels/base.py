from abc import ABC, abstractmethod
from typing import Dict
import logging

from pysentinel.core.threshold import Violation

logger = logging.getLogger(__name__)


class AlertChannel(ABC):
    """Abstract base class for channels"""

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config

    @abstractmethod
    async def send_alert(self, violation: Violation) -> bool:
        """Send alert for violation"""
        pass
