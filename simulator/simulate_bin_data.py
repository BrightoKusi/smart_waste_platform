import json 
import time
import random
from datetime import datetime
from kafka import KafkaProducer

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

def main():
    producer = KafkaProducer(
        bootstrap_servers="localhost:29092",
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',
        retries=3
    )
    
    try:
        while True:
            data = BinDataGenerator.generate_data()
            print("Sending data:", json.dumps(data, indent=2))
            producer.send("bin_status", data)
            time.sleep(Config.INTERVAL_SEC)
    except KeyboardInterrupt:
        print("\nShutting down producer...")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    main()