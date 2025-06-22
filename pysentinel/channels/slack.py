from pysentinel.core.threshold import Violation
from pysentinel.channels.base import AlertChannel, logger
from pysentinel.utils.constants import Severity


class Slack(AlertChannel):
    """Slack alert channel implementation"""

    async def send_alert(self, violation: Violation) -> bool:
        import aiohttp

        try:
            payload = {
                "channel": self.config['channel'],
                "username": self.config['username'],
                "icon_emoji": self.config['icon_emoji'],
                "text": f"🚨 *{violation.severity.value.upper()}* Alert: {violation.alert_name}",
                "attachments": [
                    {
                        "color": "danger" if violation.severity == Severity.CRITICAL else "warning",
                        "fields": [
                            {
                                "title": "Message",
                                "value": violation.message,
                                "short": False
                            },
                            {
                                "title": "Current Value",
                                "value": str(violation.current_value),
                                "short": True
                            },
                            {
                                "title": "Threshold",
                                "value": f"{violation.operator} {violation.threshold_value}",
                                "short": True
                            },
                            {
                                "title": "Datasource",
                                "value": violation.datasource_name,
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": violation.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                                "short": True
                            }
                        ]
                    }
                ]
            }

            # Add mentions if configured
            if 'mention_users' in self.config:
                payload['text'] = f"{' '.join(self.config['mention_users'])} {payload['text']}"

            async with aiohttp.ClientSession() as session:
                async with session.post(self.config['webhook_url'], json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False
