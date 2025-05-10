# Example nws text data flow dedup

## Multiple data stream parsers that do the the following

1. Read their respective streams to tokenize products
1. Condition a single product in hopes of later dedup
1. Create a JSON message with a `sha256` checksum calculated and `body` payload
1. Send this to `weather_dedup` direct queue

## A single dedup process that does the following

1. Consume messages from the `weather_dedup` direct queue.
1. Dedup based on the `sha256` checksum
1. Rewrite JSON payloads with a `timestamp` payload added to `weather_stream`,
   which is a stream queue.

## Multiple consumers that do what they need to do

1. Default to only request `1h` offset worth of data from `weather_stream`
1. Track latest processed `timestamp` value and use value at load to prevent
   duplicated processing.
1. Profit
