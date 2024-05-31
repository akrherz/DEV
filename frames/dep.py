"""Lapse."""

import click
import httpx
from tqdm import tqdm

import pandas as pd


@click.command()
@click.option("--scenario", type=int)
@click.option("--year", type=int, required=True, help="Year to process")
def main(scenario, year):
    """Go Main"""
    # can't do jan 1 as the ramp changes for single day plots :/
    dates = pd.date_range(f"{year}-01-02", f"{year}-12-31", freq="D")
    baseuri = (
        "https://mesonet-dep.agron.iastate.edu/auto/"
        f"%s0101_%s_{scenario}_avg_delivery.png?mn=1&progressbar=1&cruse=1"
    )

    stepi = 0
    progress = tqdm(dates)
    for now in progress:
        progress.set_description(f"{now:%Y-%m-%d}")
        url = baseuri % (now.year, now.strftime("%Y%m%d"))
        req = httpx.get(url, timeout=60)
        if req.status_code != 200:
            print(f"Failed with {req.status_code} to fetch {url}")
            continue
        with open(f"images/{now:%Y}_{stepi:05.0f}_{scenario}.png", "wb") as fh:
            fh.write(req.content)
        stepi += 1


if __name__ == "__main__":
    main()
