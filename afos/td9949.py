"""Process really old files from NCEI.

https://www1.ncdc.noaa.gov/pub/data/documentlibrary/tddoc/td9949.pdf
"""
from io import BytesIO
import struct


def persist(record):
    """Save to the database!"""
    print("_" * 80)
    print(f"cccnnnxxx {record['cccnnnxxx']}")
    print(record["text"])
    print("_" * 80)


def main():
    """Go Main Go."""
    fd = open("9949dec1989-22", "rb")
    current = {}
    while True:
        record = BytesIO(fd.read(284))
        if len(record.getvalue()) != 284:
            print(f"read() resulted in len: {len(record.getvalue())}")
            break
        # Ignore LTH and LAF
        record.read(29)

        meat = (
            record.read(284 - 29)
            .decode("ascii", "replace")
            .replace("\x00", "")
        )
        if len(meat) == 0:
            continue
        # If ETX is present, this terminates the ongoing product
        etx = ord(meat[-1]) == 65533
        # Attempt to compute a CCCNNNXXX, maybe unused for some
        cccnnnxxx = b"".join(struct.unpack("9c", record.getvalue()[35:44]))

        # Record type A (first of multi-block)
        if not etx and not current:
            print("Found A")
            current = {
                "cccnnnxxx": cccnnnxxx,
                "text": meat[20:],  # -2 byte variance from docs
            }
        # Record type B (intermediate)
        elif not etx and current:
            print("Found B")
            current["text"] += meat[2:]  # -1 byte variance from docs
        # Record type C (last block)
        elif etx and current:
            print("Found C")
            current["text"] += meat[2:-1]
            persist(current)
            current = {}
        # Record type D (single block)
        elif etx and not current:
            print("Found D")
            current = {
                "cccnnnxxx": cccnnnxxx,
                "text": meat[20:-1],  # -2 byte variance from docs
            }
            persist(current)
            current = {}
        # Record type E (unknown, toss it)
        else:
            print("Found E")
            continue


if __name__ == "__main__":
    main()
