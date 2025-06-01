import json
import logging
from kafka import KafkaConsumer
import psycopg2
from psycopg2 import pool, errors

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

# Database configuration
DB_CONFIG = {
    "dbname": "smart_waste",
    "user": "waste_user",
    "password": "waste_pass",
    "host": "localhost",
    "port": "5432"
}

# Create connection pool
try:
    connection_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        **DB_CONFIG
    )
    logger.info("Successfully created database connection pool")
except Exception as e:
    logger.error(f"Error creating connection pool: {e}")
    raise

# Initialize database schema
def initialize_database():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS bin_status (
        id SERIAL PRIMARY KEY,
        bin_id VARCHAR(50) NOT NULL,
        latitude DECIMAL(10, 6) NOT NULL,
        longitude DECIMAL(10, 6) NOT NULL,
        fill_level DECIMAL(5, 2) NOT NULL,
        temperature DECIMAL(5, 2) NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_bin_id ON bin_status(bin_id);
    CREATE INDEX IF NOT EXISTS idx_timestamp ON bin_status(timestamp);
    """
    
    try:
        conn = connection_pool.getconn()
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
            conn.commit()
            logger.info("Database tables and indexes created successfully")
    except errors.DuplicateTable:
        logger.info("Tables already exist")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        if conn:
            connection_pool.putconn(conn)

# Process Kafka messages
def process_messages():
    consumer = KafkaConsumer(
        "bin_status",
        bootstrap_servers='localhost:29092',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='bin-status-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=10000  # Timeout if no messages
    )

    logger.info('Listening to bin_status topic...')

    try:
        for message in consumer:
            try:
                data = message.value
                logger.info(f'Received message: {json.dumps(data, indent=2)}')

                insert_query = """
                INSERT INTO bin_status(
                    bin_id, latitude, longitude, 
                    fill_level, temperature, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data["bin_id"],
                    data["location"]["lat"],
                    data["location"]["lon"],
                    data["fill_level"],
                    data["temperature"],
                    data["timestamp"]
                )

                conn = connection_pool.getconn()
                with conn.cursor() as cursor:
                    cursor.execute(insert_query, values)
                    conn.commit()
                    logger.debug("Successfully inserted record")

            except KeyError as e:
                logger.error(f"Missing field in message: {e}")
            except errors.Error as e:
                logger.error(f"Database error: {e}")
                conn.rollback()
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
            finally:
                if conn:
                    connection_pool.putconn(conn)

    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    except Exception as e:
        logger.error(f"Consumer error: {e}")
    finally:
        consumer.close()
        logger.info("Kafka consumer closed")

if __name__ == "__main__":
    initialize_database()
    process_messages()