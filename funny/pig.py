import time
import datetime

while True:
    print(" " * int((datetime.datetime.now().microsecond / 100) % 6), end="")
    print("🐖")
    time.sleep(0.2)
