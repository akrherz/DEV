"""Example producer for weather data feed.

This producer sends to the input exchange for deduplication.
"""

import json
import time
from hashlib import sha256

import pika
from pyiem.util import utc


def get_connection():
    """Get a connection to RabbitMQ."""
    return pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))


def main():
    """Run producer."""
    connection = get_connection()
    channel = connection.channel()

    # Declare the input exchange
    channel.exchange_declare(
        exchange="weather_input",
        exchange_type="direct",  # Using direct exchange
        durable=True,
    )

    while True:
        # create a text message that will likely be duplicated
        body = f"Weather data at {utc():%Y-%m-%d %H:%M}"
        message = {
            "sha256": sha256(body.encode()).hexdigest(),
            "body": body,
        }

        # Publish to input exchange with specific routing key
        channel.basic_publish(
            exchange="weather_input",
            routing_key="weather",  # Must match the queue binding
            body=json.dumps(message).encode(),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ),
        )
        print(f"Sent message: {body}")
        time.sleep(2)


if __name__ == "__main__":
    main()
