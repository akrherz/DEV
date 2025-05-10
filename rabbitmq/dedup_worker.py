"""RabbitMQ deduplication worker.

This script consumes from multiple producers, deduplicates messages,
and publishes to a stream queue for consumers.
"""

import asyncio
import json
import time
from typing import Dict, Set

from aio_pika import connect_robust
from pyiem.util import utc
from rstream import AMQPMessage, Producer


class DedupWorker:
    """Handles deduplication of messages from multiple producers."""

    def __init__(self):
        """Initialize the worker."""
        # Hash window for deduplication (5 minute window)
        self.seen_hashes: Dict[float, Set[str]] = {}
        self.window_size = 300  # 5 minutes in seconds
        self.connection = None
        self.channel = None
        self.stream_producer = None
        self.queue = None

    async def setup(self):
        """Setup connections and declare queues."""
        # Setup AMQP connection for input
        self.connection = await connect_robust("amqp://guest:guest@localhost/")
        self.channel = await self.connection.channel()

        # Declare input exchange and queue
        exchange = await self.channel.declare_exchange(
            "weather_input", type="direct", durable=True
        )
        self.queue = await self.channel.declare_queue(
            "weather_dedup",
            durable=True,
            arguments={"x-single-active-consumer": True},
        )
        await self.queue.bind(exchange=exchange, routing_key="weather")

        # Setup stream producer
        self.stream_producer = Producer(
            "localhost", username="guest", password="guest"
        )
        # Create stream if it doesn't exist
        await self.stream_producer.create_stream(
            "weather_stream", exists_ok=True
        )

    def cleanup_old_hashes(self, current_time: float) -> None:
        """Remove hashes older than the window size."""
        cutoff_time = current_time - self.window_size
        old_times = [t for t in self.seen_hashes if t < cutoff_time]
        for t in old_times:
            del self.seen_hashes[t]

    def is_duplicate(self, message_hash: str) -> bool:
        """Check if message is a duplicate within the time window."""
        current_time = time.time()
        self.cleanup_old_hashes(current_time)

        # Check if hash exists in any recent window
        for hashes in self.seen_hashes.values():
            if message_hash in hashes:
                return True

        # Not a duplicate, add to current window
        self.seen_hashes.setdefault(current_time, set()).add(message_hash)
        return False

    async def process_message(self, message):
        """Handle incoming messages."""
        try:
            body = message.body.decode()
            data = json.loads(body)
            message_hash = data["sha256"]

            # Check for duplicates
            if not self.is_duplicate(message_hash):
                # Add timestamp to message before publishing
                data["timestamp"] = utc().isoformat()
                # Not a duplicate, publish to stream with timestamp
                amqp_message = AMQPMessage(body=json.dumps(data).encode())
                await self.stream_producer.send(
                    stream="weather_stream",
                    publisher_name="dedup_worker",
                    message=amqp_message,
                )
                print(f"Published message {message_hash}")
            else:
                print(f"Dropped duplicate message: {message_hash}")

        except Exception as exc:
            print(f"Error processing message: {exc}")
        finally:
            await message.ack()

    async def run(self):
        """Start consuming messages."""
        if not self.connection:
            await self.setup()

        # Start consuming with prefetch
        await self.channel.set_qos(prefetch_count=100)
        print("Starting deduplication worker...")

        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self.process_message(message)


async def main():
    """Run the worker."""
    worker = DedupWorker()
    try:
        await worker.run()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        if worker.connection:
            await worker.connection.close()


if __name__ == "__main__":
    asyncio.run(main())
