import json 
import time
import random
from datetime import datetime

from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:29092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',  
    retries=3,   
    linger_ms=100 
)

BIN_IDS = [f"BIN_{i:03}" for i in range(1, 6)]

def generate_data():
    return {
        "bin_id": random.choice(BIN_IDS),
        "location": {
            "lat": round(random.uniform(5.5, 5.7), 6),
            "lon": round(random.uniform(-0.3, -0.1), 6)
        },
        "fill_level": round(random.uniform(10, 100), 2),
        "temperature": round(random.uniform(20, 60), 2),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    while True:
        data = generate_data()
        print("Sending data:", json.dumps(data, indent=2))
        producer.send("bin_status", data)
        time.sleep(3)
        producer.flush()
