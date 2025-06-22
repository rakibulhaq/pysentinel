from pysentinel.core.threshold import Violation
from pysentinel.channels.base import AlertChannel, logger


class Telegram(AlertChannel):
    """Telegram alert channel implementation"""

    async def send_alert(self, violation: Violation) -> bool:
        import aiohttp

        try:
            payload = {
                "chat_id": self.config['chat_id'],
                "text": f"🚨 *{violation.severity.value.upper()}* Alert: {violation.alert_name}\n"
                        f"Message: {violation.message}\n"
                        f"Current Value: {violation.current_value}\n"
                        f"Threshold: {violation.operator} {violation.threshold_value}\n"
                        f"Datasource: {violation.datasource_name}\n"
                        f"Time: {violation.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
                "parse_mode": "Markdown",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.config['webhook_url'], json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
