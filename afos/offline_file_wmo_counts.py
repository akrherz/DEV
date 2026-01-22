"""Figure out why so big.

Note that id3b has feedtype=11 telemetry logging already.
"""

import click
from pyiem.wmo import WMOProduct
from tqdm import tqdm


@click.command()
@click.option("--filename", default=None, help="Filename to process")
def main(filename: str):
    """Go"""
    failures = 0
    progress = tqdm()
    totals = {}
    with open(filename, "rb") as fh:
        for token in fh.read().split(b"\001\r\r\n"):
            if not token.strip():
                continue
            try:
                prod = WMOProduct(
                    token.strip().decode("ascii", errors="ignore")
                )
            except Exception:
                print(repr(token[:30]))
                failures += len(token)
                continue
            progress.update()
            progress.set_description(f"Failures: {failures}")
            if prod.wmo not in totals:
                totals[prod.wmo] = 0
            totals[prod.wmo] += len(token)

    # Print top 10 largest
    sorted_totals = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    print("WMO Code       Total Size (MB)")
    print("-------------------------------")
    for wmo, size in sorted_totals[:10]:
        print(f"{wmo:10s} {size / 1_000_000:.2f}")


if __name__ == "__main__":
    main()
