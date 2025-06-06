import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError, NoBrokersAvailable

# Configuration class
class Config:
    BIN_IDS = [f"BIN_{i:03}" for i in range(1, 6)]
    LOCATION_RANGES = {
        "min_lat": 5.5, "max_lat": 5.7,
        "min_lon": -0.3, "max_lon": -0.1
    }
    TEMP_RANGE = (20, 60)
    FILL_RANGE = (10, 100)
    INTERVAL_SEC = 3
    KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"  
    TOPIC_NAME = "bin_status"
    MAX_RETRIES = 5
    RETRY_DELAY = 5  


# Generate simulated bin data
class BinDataGenerator:
    @staticmethod
    def generate_data():
        return {
            "bin_id": random.choice(Config.BIN_IDS),
            "location": {
                "lat": round(random.uniform(
                    Config.LOCATION_RANGES["min_lat"],
                    Config.LOCATION_RANGES["max_lat"]
                ), 6),
                "lon": round(random.uniform(
                    Config.LOCATION_RANGES["min_lon"],
                    Config.LOCATION_RANGES["max_lon"]
                ), 6)
            },
            "fill_level": round(random.uniform(*Config.FILL_RANGE), 2),
            "temperature": round(random.uniform(*Config.TEMP_RANGE), 2),
            "battery_level": round(random.uniform(20, 100), 2),
            "status": random.choice(["OK", "WARNING", "ERROR"]),
            "timestamp": datetime.utcnow().isoformat()
        }

# Create Kafka topic with retry logic
def create_kafka_topic():
    retries = 0
    while retries < Config.MAX_RETRIES:
        try:
            admin = KafkaAdminClient(
                bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
                client_id="bin-simulator"
            )

            topic = NewTopic(
                name=Config.TOPIC_NAME,
                num_partitions=3,
                replication_factor=1
            )

            admin.create_topics([topic])
            print(f"Topic '{Config.TOPIC_NAME}' created.")
            admin.close()
            return
        except TopicAlreadyExistsError:
            print(f"Topic '{Config.TOPIC_NAME}' already exists.")
            return
        except (KafkaError, NoBrokersAvailable) as e:
            retries += 1
            print(f"[Retry {retries}/{Config.MAX_RETRIES}] Kafka not ready: {e}")
            time.sleep(Config.RETRY_DELAY)

    print("Failed to connect to Kafka after several retries.")
    exit(1)

# Main simulation loop
def main():
    print("Starting Smart Bin Simulator...")
    create_kafka_topic()

    try:
        producer = KafkaProducer(
            bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
        )
    except Exception as e:
        print(f"Failed to create KafkaProducer: {e}")
        return

    try:
        while True:
            data = BinDataGenerator.generate_data()
            print("Sending data:", json.dumps(data, indent=2))

            try:
                future = producer.send(Config.TOPIC_NAME, data)
                result = future.get(timeout=10)
                print(f"Delivered to partition {result.partition}, offset {result.offset}")
            except Exception as send_error:
                print(f"Failed to send message: {send_error}")

            time.sleep(Config.INTERVAL_SEC)
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    finally:
        producer.flush()
        producer.close()
        print("Kafka producer closed.")

if __name__ == "__main__":
    main()
