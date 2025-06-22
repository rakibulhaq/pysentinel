import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pysentinel.core.threshold import Violation
from pysentinel.channels.base import AlertChannel, logger


class Email(AlertChannel):
    """Email alert notifier implementation"""

    async def send_alert(self, violation: Violation) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['from_address']
            msg['To'] = ', '.join(self.config['recipients'])
            msg['Subject'] = self.config['subject_template'].format(alert_title=violation.alert_name)

            body = f"""
            Alert: {violation.alert_name}
            Severity: {violation.severity.value.upper()}
            Message: {violation.message}
            Current Value: {violation.current_value}
            Threshold: {violation.operator} {violation.threshold_value}
            Datasource: {violation.datasource_name}
            Time: {violation.timestamp}
            """

            msg.attach(MIMEText(body, 'plain'))

            password = self.config['password']
            if password.startswith('${') and password.endswith('}'):
                env_var = password[2:-1]
                password = os.getenv(env_var, password)

            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['username'], password)
            text = msg.as_string()
            server.sendmail(self.config['from_address'], self.config['recipients'], text)
            server.quit()

            return True
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
