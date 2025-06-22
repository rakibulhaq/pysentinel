import os
from typing import Dict, Any

from pysentinel.datasources.base import DataSource, logger
from pysentinel.utils.exception import DataSourceException


class RedisDataSource(DataSource):
    """Redis data source implementation"""

    async def connect(self):
        if not self._connection:
            import aioredis
            password = self.config.get('password', '')
            if password.startswith('${') and password.endswith('}'):
                env_var = password[2:-1]
                password = os.getenv(env_var, password)

            self._connection = await aioredis.from_url(
                f"redis://:{password}@{self.config['host']}:{self.config['port']}/{self.config['db']}"
            )

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def fetch_data(self, query: str) -> Dict[str, Any]:
        await self.connect()
        try:
            if query == "INFO stats":
                info = await self._connection.info("stats")
                hit_rate = (info.get('keyspace_hits', 0) / max(
                    info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)) * 100
                return {"hit_rate": hit_rate}
            elif query == "INFO memory":
                info = await self._connection.info("memory")
                return {"memory_usage": info.get('used_memory_rss', 0)}
            elif query == "INFO clients":
                info = await self._connection.info("clients")
                return {"connected_clients": info.get('connected_clients', 0)}
            else:
                return {}
        except Exception as e:
            logger.error(f"Error executing Redis query: {e}")
            raise DataSourceException(f"Redis query failed: {e}")