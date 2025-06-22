import asyncio
import os

from pysentinel.core.threshold import Violation
from pysentinel.channels.base import AlertChannel, logger


class Webhook(AlertChannel):
    """Webhook alert notifier implementation"""

    async def send_alert(self, violation: Violation) -> bool:
        import aiohttp

        try:
            headers = self.config.get('headers', {})
            # Replace environment variables in headers
            for key, value in headers.items():
                if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    headers[key] = os.getenv(env_var, value)

            payload = violation.to_dict()

            async with aiohttp.ClientSession() as session:
                for attempt in range(self.config.get('retry_count', 1)):
                    try:
                        async with session.request(
                                self.config.get('method', 'POST'),
                                self.config['url'],
                                json=payload,
                                headers=headers
                        ) as response:
                            if response.status < 400:
                                return True
                    except Exception as e:
                        if attempt == self.config.get('retry_count', 1) - 1:
                            raise e
                        await asyncio.sleep(1)

            return False
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False
