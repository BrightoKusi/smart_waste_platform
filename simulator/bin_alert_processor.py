import json
import smtplib
import os
import logging
from email.mime.text import MIMEText
from kafka import KafkaConsumer
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# Embedded AlertRules class
class AlertRules:
    TEMPERATURE_THRESHOLD = 50
    FILL_LEVEL_THRESHOLD = 90
    BATTERY_LEVEL_THRESHOLD = 30

    @classmethod
    def check(cls, data):
        alerts = []

        if data.get("temperature", 0) > cls.TEMPERATURE_THRESHOLD:
            alerts.append(f"High temperature: {data['temperature']}°C")

        if data.get("fill_level", 0) > cls.FILL_LEVEL_THRESHOLD:
            alerts.append(f"Bin is almost full: {data['fill_level']}%")

        if data.get("battery_level", 100) < cls.BATTERY_LEVEL_THRESHOLD:
            alerts.append(f"Low battery: {data['battery_level']}%")

        if data.get("status", "OK") == "ERROR":
            alerts.append("Sensor reported an ERROR")

        return alerts

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("ALERT_EMAIL_FROM")
        self.to_email = os.getenv("ALERT_EMAIL_TO")

    def send_alert(self, bin_id, alerts, timestamp):
        subject = f"ALERT for Bin {bin_id}"
        body = f"The following alerts were triggered at {timestamp}:\n\n" + "\n".join(alerts)
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = self.to_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            logger.info(f"Alert email sent for bin {bin_id}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

class KafkaAlertProcessor:
    def __init__(self):
        self.consumer = KafkaConsumer(
            "bin_status",
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092"),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="bin-alert-processor",
            value_deserializer=lambda x: json.loads(x.decode("utf-8"))
        )
        self.notifier = EmailNotifier()

    def run(self):
        logger.info("Alert processor started...")
        for message in self.consumer:
            data = message.value
            bin_id = data.get("bin_id", "UNKNOWN")
            timestamp = data.get("timestamp", str(datetime.utcnow()))
            alerts = AlertRules.check(data)

            if alerts:
                logger.info(f"Alerts triggered for {bin_id}: {alerts}")
                self.notifier.send_alert(bin_id, alerts, timestamp)
            else:
                logger.debug(f"No alerts for {bin_id} at {timestamp}")

if __name__ == "__main__":
    processor = KafkaAlertProcessor()
    processor.run()
