import json
import logging
import os
import psycopg2
from kafka import KafkaConsumer
from psycopg2 import pool, errors
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('consumer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT")
        )
        self.initialize_schema()

    def initialize_schema(self):
        schema = """
        CREATE TABLE IF NOT EXISTS bin_status (
            id SERIAL PRIMARY KEY,
            bin_id VARCHAR(50) NOT NULL,
            latitude DECIMAL(10, 6) NOT NULL,
            longitude DECIMAL(10, 6) NOT NULL,
            fill_level DECIMAL(5, 2) NOT NULL,
            temperature DECIMAL(5, 2) NOT NULL,
            battery_level DECIMAL(5, 2),
            status VARCHAR(20) DEFAULT 'OK',
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_bin_id ON bin_status(bin_id);
        CREATE INDEX IF NOT EXISTS idx_timestamp ON bin_status(timestamp);
        CREATE INDEX IF NOT EXISTS idx_status ON bin_status(status);
        """
        
        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute(schema)
                conn.commit()
                logger.info("Database schema initialized")
        except errors.DuplicateTable:
            logger.info("Tables already exist")
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def save_message(self, data):
        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO bin_status(
                        bin_id, latitude, longitude,
                        fill_level, temperature,
                        battery_level, status,
                        timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        data["bin_id"],
                        data["location"]["lat"],
                        data["location"]["lon"],
                        data["fill_level"],
                        data["temperature"],
                        data.get("battery_level"),
                        data.get("status", "OK"),
                        data["timestamp"]
                    ))
                conn.commit()
                logger.debug(f"Inserted data for bin {data['bin_id']}")
                return True
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.connection_pool.putconn(conn)

class KafkaMessageConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            "bin_status",
            bootstrap_servers="kafka:9092",  # Docker service name
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="bin-status-group",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            consumer_timeout_ms=10000
        )
        self.db = DatabaseManager()

    def validate_message(self, data):
        required_fields = {
            "bin_id": str,
            "location": dict,
            "fill_level": (int, float),
            "temperature": (int, float),
            "timestamp": str
        }
        
        for field, field_type in required_fields.items():
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(data[field], field_type):
                raise ValueError(f"Invalid type for {field}")
        
        if "lat" not in data["location"] or "lon" not in data["location"]:
            raise ValueError("Location missing lat/lon coordinates")

    def process_messages(self):
        logger.info("Starting Kafka consumer...")
        try:
            for message in self.consumer:
                try:
                    data = message.value
                    self.validate_message(data)
                    
                    if not self.db.save_message(data):
                        logger.warning(f"Failed to process message: {data['bin_id']}")
                    else:
                        logger.info(f"Processed bin {data['bin_id']} at {data['timestamp']}")
                        
                except ValueError as e:
                    logger.error(f"Invalid message: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Shutting down consumer...")
        finally:
            self.consumer.close()
            logger.info("Consumer stopped")

if __name__ == "__main__":
    consumer = KafkaMessageConsumer()
    consumer.process_messages()