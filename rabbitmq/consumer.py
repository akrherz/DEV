"""Example RabbitMQ Stream Consumer using Pika.

This script demonstrates consuming messages from a RabbitMQ stream.
"""

import argparse
import json

import pika


def get_connection():
    """Get a connection to RabbitMQ."""
    return pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))


def main(consumer_name="consumer1", offset="last"):
    """Run main.

    Args:
        consumer_name: unique name for this consumer
        offset: either 'first' or 'last' for positioning
    """
    last_stamp = ""
    try:
        with open(f"{consumer_name}.last", "r") as f:
            last_stamp = f.read().strip()
    except FileNotFoundError:
        print(f"File {consumer_name}.last not found, starting from beginning.")

    def callback(ch, method, properties, body):
        """Handle incoming messages."""
        try:
            data = json.loads(body)
            stamp = data.get("timestamp")
            if stamp is None:
                print(
                    f"Consumer {consumer_name}: "
                    f"No timestamp in message {data.get('sha256')}"
                )
                ch.basic_nack(delivery_tag=method.delivery_tag)
                return
            if stamp <= last_stamp:
                print(
                    f"Consumer {consumer_name}: "
                    f"Dropping message {data.get('sha256')}"
                )
                ch.basic_nack(delivery_tag=method.delivery_tag)
                return
            with open(f"{consumer_name}.last", "w") as f:
                f.write(stamp)
            print(
                f"Consumer {consumer_name}: Received message "
                f"{data.get('sha256')} {data['body']} {stamp}"
            )
        except Exception as exp:
            print(f"Error processing message: {exp}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    connection = get_connection()
    channel = connection.channel()

    # Declare stream queue (should already exist)
    channel.queue_declare(
        queue="weather_stream",
        durable=True,
        arguments={"x-queue-type": "stream"},
    )

    # Configure consumer with unique group for independent offset tracking
    channel.basic_qos(prefetch_count=100)
    # Configure stream consumption with consumer-specific group
    group_id = f"weather_consumer_{consumer_name}"
    stream_args = {
        "x-group-id": group_id,  # Unique group per consumer
        "x-stream-offset": offset,
    }

    channel.basic_consume(
        queue="weather_stream",
        on_message_callback=callback,
        consumer_tag=consumer_name,
        arguments=stream_args,
    )

    print(f"Starting {consumer_name} with offset:`{offset}`. CTRL+C to exit")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather Stream Consumer")
    parser.add_argument(
        "--name", default="consumer1", help="Unique consumer name"
    )
    parser.add_argument(
        "--offset",
        choices=["first", "last", "1h"],
        default="1h",
        help="Where to start first=all messages, last=recent messages",
    )
    args = parser.parse_args()
    main(args.name, args.offset)
