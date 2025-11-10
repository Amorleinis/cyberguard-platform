import argparse
import json
from confluent_kafka import Producer
from events import get_event_template, interactive_edit
from schemas import EVENT_MODEL_MAP
from pydantic import ValidationError

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered message to {msg.topic()} [{msg.partition()}]")

def main():
    parser = argparse.ArgumentParser(description="Spectra Phoenix Kafka Event Producer CLI")
    parser.add_argument("--bootstrap-server", default="localhost:9092", help="Kafka bootstrap server")
    args = parser.parse_args()

    topic_map = {
        "process_start": "process-events",
        "process_stop": "process-events",
        "file_access": "file-events",
        "network_connection": "network-events",
        "alert": "alert-events",
    }

    producer = Producer({'bootstrap.servers': args.bootstrap_server})

    print("Available event types:", ", ".join(topic_map.keys()))
    print("Type 'quit' to exit.")

    while True:
        event_type = input("Enter event type: ").strip()
        if event_type == "quit":
            break
        if event_type not in topic_map:
            print("Unknown event type. Try again.")
            continue

        event = get_event_template(event_type)
        if not event:
            print(f"No template for event type {event_type}")
            continue

        event = interactive_edit(event)

        # Validate event against schema
        try:
            model_cls = EVENT_MODEL_MAP[event_type]
            validated = model_cls.parse_obj(event)
            event_json = validated.json()
        except ValidationError as e:
            print("Validation error:", e)
            continue

        producer.produce(topic_map[event_type], event_json.encode('utf-8'), callback=delivery_report)
        producer.poll(0)
        print(f"Sent event type {event_type} to topic {topic_map[event_type]}")

    producer.flush()

if __name__ == "__main__":
    main()
