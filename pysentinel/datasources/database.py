from typing import Dict, Any

from pysentinel.datasources.base import DataSource, logger
from pysentinel.utils.exception import DataSourceException


class PostgreSQLDataSource(DataSource):
    """PostgreSQL data source implementation"""

    async def connect(self):
        if not self._connection:
            import asyncpg
            self._connection = await asyncpg.connect(self.config['connection_string'])

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def fetch_data(self, query: str) -> Dict[str, Any]:
        await self.connect()
        try:
            result = await self._connection.fetchrow(query)
            return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Error executing PostgreSQL query: {e}")
            raise DataSourceException(f"PostgreSQL query failed: {e}")