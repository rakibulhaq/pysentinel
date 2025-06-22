import os
from typing import Dict, Any

from pysentinel.datasources.base import DataSource, logger
from pysentinel.utils.exception import DataSourceException


class HTTPDataSource(DataSource):
    """HTTP API data source implementation"""

    async def connect(self):
        # HTTP doesn't need persistent connection
        pass

    async def close(self):
        pass

    async def fetch_data(self, query: str) -> Dict[str, Any]:
        import aiohttp
        url = f"{self.config['base_url']}{query}"
        headers = self.config.get('headers', {})

        # Replace environment variables in headers
        for key, value in headers.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                headers[key] = os.getenv(env_var, value)

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.connection_timeout)) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        raise DataSourceException(f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            logger.error(f"Error fetching from HTTP API: {e}")
            raise DataSourceException(f"HTTP fetch failed: {e}")