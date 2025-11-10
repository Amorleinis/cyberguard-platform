import threading
import time
import random
from spectra_phoenix_producer.events import get_event_template
from spectra_phoenix_producer.schemas import EVENT_MODEL_MAP
from confluent_kafka import Producer
import json
from pydantic import ValidationError

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

TOPIC_MAP = {
    "process_start": "process-events",
    "process_stop": "process-events",
    "file_access": "file-events",
    "network_connection": "network-events",
    "alert": "alert-events",
}

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered message to {msg.topic()} [{msg.partition()}]")

def produce_event(producer, event_type, interval_sec=1.0):
    while True:
        event = get_event_template(event_type)
        try:
            model_cls = EVENT_MODEL_MAP[event_type]
            validated = model_cls.parse_obj(event)
            event_json = validated.json()
            producer.produce(TOPIC_MAP[event_type], event_json.encode('utf-8'), callback=delivery_report)
            producer.poll(0)
        except ValidationError as e:
            print(f"Validation error in {event_type}: {e}")
        time.sleep(interval_sec)

def main():
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

    threads = []
    event_intervals = {
        "process_start": 1.5,
        "process_stop": 3.0,
        "file_access": 2.0,
        "network_connection": 1.0,
        "alert": 10.0,
    }

    for event_type, interval in event_intervals.items():
        t = threading.Thread(target=produce_event, args=(producer, event_type, interval), daemon=True)
        threads.append(t)
        t.start()

    print("Test harness running... Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()
