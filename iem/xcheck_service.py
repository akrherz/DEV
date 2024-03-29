"""Send URLs through prod and dev to check for differences."""

import random
from pathlib import Path

import click
import httpx
from tqdm import tqdm


@click.command()
@click.option(
    "--filename",
    type=click.Path(path_type=Path),
    help="Apache log file to review",
)
@click.option(
    "--size",
    type=int,
    default=1000,
    help="Number of lines to randomly sample",
)
def main(filename, size):
    """Go Main Go."""
    with open(filename) as fh:
        lines = fh.readlines()[::-1]
    # Randomly sample the lines
    lines = random.sample(lines, min(len(lines), size))
    for line in tqdm(lines):
        uri = line.split()[6]
        req = httpx.get(f"https://mesonet.agron.iastate.edu{uri}", timeout=300)
        ans_status = req.status_code
        ans_lines = len(req.text.split("\n"))
        req = httpx.get(f"http://iem.local{uri}", timeout=300)
        dev_status = req.status_code
        if dev_status == 422:
            print(req.text)
        dev_lines = len(req.text.split("\n"))
        if ans_status != dev_status or ans_lines != dev_lines:
            print(f"{uri} {ans_status} {ans_lines} {dev_status} {dev_lines}")
            return


if __name__ == "__main__":
    main()
