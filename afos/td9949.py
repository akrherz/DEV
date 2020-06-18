"""Process really old files from NCEI.

https://www1.ncdc.noaa.gov/pub/data/documentlibrary/tddoc/td9949.pdf
"""
from io import BytesIO
import struct


def main():
    """Go Main Go."""
    fd = open("/mesonet/tmp/ncei/9949dec1989-28", "rb")
    while True:
        header = BytesIO(fd.read(256))
        print(f"New month: {struct.unpack('B', header.read(1))}")
        while True:
            record = BytesIO(fd.read(284))
            if len(record.getvalue()) != 284:
                print(len(record.getvalue()))
                break
            record.read(16)
            eom = struct.unpack("B", record.read(1))
            print(eom)
            sys.exit()


if __name__ == "__main__":
    main()
