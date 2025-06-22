from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataSource(ABC):
    """Abstract base class for data sources"""

    def __init__(self, name: str, config: Dict, **kwargs):
        self.interval = config.get('interval', 60)  # Default to 60 seconds
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', False)
        self.last_fetch_time = None
        self.error_count = 0
        self.max_errors = config.get('max_retries', 5)
        self.connection_timeout = config.get('timeout', 30)
        self._connection = None

    @abstractmethod
    async def fetch_data(self, query: str) -> Dict[str, Any]:
        """Fetch data from the source"""
        pass

    @abstractmethod
    async def connect(self):
        """Establish connection to the data source"""
        pass

    @abstractmethod
    async def close(self):
        """Close connection to the data source"""
        pass

    async def health_check(self) -> bool:
        """Check if the data source is healthy"""
        try:
            await self.connect()
            return True
        except Exception as e:
            logger.warning(f"Health check failed for {self.name}: {e}")
            return False

    def should_fetch(self) -> bool:
        """Check if it's time to fetch data"""
        if not self.enabled:
            return False

        if self.last_fetch_time is None:
            return True

        return (datetime.now() - self.last_fetch_time).total_seconds() >= self.interval
