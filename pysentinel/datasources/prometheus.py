from typing import Dict, Any

from pysentinel.datasources.base import DataSource, logger
from pysentinel.utils.exception import DataSourceException


class PrometheusDataSource(DataSource):
    """Prometheus data source implementation"""

    async def connect(self):
        pass

    async def close(self):
        pass

    async def fetch_data(self, query: str) -> Dict[str, Any]:
        import aiohttp
        url = f"{self.config['url']}/api/v1/query"
        params = {'query': query}

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.connection_timeout)) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['status'] == 'success':
                            result = data['data']['result']
                            if result:
                                metric_name = query.split('(')[0].replace('avg', '').strip()
                                value = float(result[0]['value'][1])
                                return {metric_name: value}
                        return {}
                    else:
                        raise DataSourceException(f"Prometheus HTTP {response.status}")
        except Exception as e:
            logger.error(f"Error fetching from Prometheus: {e}")
            raise DataSourceException(f"Prometheus query failed: {e}")