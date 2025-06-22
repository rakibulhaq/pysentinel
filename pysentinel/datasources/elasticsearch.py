import json
from typing import Dict, Any

from pysentinel.datasources.base import DataSource, logger
from pysentinel.utils.exception import DataSourceException
from elasticsearch import AsyncElasticsearch


class ElasticsearchDataSource(DataSource):
    """Elasticsearch data source implementation"""

    async def connect(self):
        if not self._connection:
            self._connection = AsyncElasticsearch(
                self.config['hosts'],
            )

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def fetch_data(self, query: str) -> Dict[str, Any]:
        await self.connect()
        try:
            query_dict = json.loads(query)
            result = await self._connection.search(
                index=self.config['index_pattern'],
                body=query_dict
            )

            # Extract aggregation results
            metrics = {}
            if 'aggregations' in result:
                for agg_name, agg_result in result['aggregations'].items():
                    if 'value' in agg_result:
                        metrics[agg_name] = agg_result['value']
                    elif 'doc_count' in agg_result:
                        metrics[agg_name] = agg_result['doc_count']

            return metrics
        except Exception as e:
            logger.error(f"Error executing Elasticsearch query: {e}")
            raise DataSourceException(f"Elasticsearch query failed: {e}")