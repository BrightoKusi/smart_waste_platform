import json
import smtplib
import os
import logging
import psycopg2
from psycopg2 import sql
from email.mime.text import MIMEText
from kafka import KafkaConsumer
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#-------------LOGGING ALERT TO POSTGRESQL TABLE ------------------------
class AlertLogger:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        self.conn.autocommit = True
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS bin_alerts (
                        id SERIAL PRIMARY KEY,
                        bin_id VARCHAR(100),
                        timestamp TIMESTAMP,
                        alert TEXT
                    );
                """)
            logger.info("Ensured bin_alerts table exists.")
        except Exception as e:
            logger.error(f"Error creating table: {e}")

    def log(self, bin_id, timestamp, alerts):
        try:
            with self.conn.cursor() as cur:
                for alert in alerts:
                    cur.execute(
                        "INSERT INTO bin_alerts (bin_id, timestamp, alert) VALUES (%s, %s, %s)",
                        (bin_id, timestamp, alert)
                    )
            logger.info(f"Logged alerts for bin {bin_id} to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to log alerts to DB: {e}")


#---------------- SENDING EMAIL ALERTS ----------------------------------
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
        self.logger = AlertLogger()

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
                self.logger.log(bin_id, timestamp, alerts)
            else:
                logger.debug(f"No alerts for {bin_id} at {timestamp}")

if __name__ == "__main__":
    processor = KafkaAlertProcessor()
    processor.run()
