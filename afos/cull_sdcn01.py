"""Fix some bloated archive files."""

import os
from io import BytesIO

import pandas as pd


def main():
    """Go Main Go."""
    for dt in pd.date_range("2025/08/19", "2025/09/24", freq="1d"):
        print(dt)
        os.system(
            f"tar -xzf /mesonet/ARCHIVE/raw/noaaport/2025/{dt:%Y%m%d}.tgz"
        )
        for hr in range(24):
            valid = dt.replace(hour=hr)
            bio = BytesIO()
            with (
                open(f"{valid:%Y%m%d%H}.txt", "rb") as fin,
                open(f"{valid:%Y%m%d%H}.txt2", "wb") as fout,
            ):
                for line in fin:
                    if line.find(b"\003\001\r\r\n") == 0:
                        msg = bio.getvalue()
                        if msg[:100].find(b"SDCN01") == -1:
                            fout.write(msg)
                        bio = BytesIO()
                    bio.write(line)
                msg = bio.getvalue()
                fout.write(msg)
            os.system(f"mv {valid:%Y%m%d%H}.txt2 {valid:%Y%m%d%H}.txt")


if __name__ == "__main__":
    main()
