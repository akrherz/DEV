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
@click.option(
    "--status-only",
    is_flag=True,
    help="Only check status code, not content",
)
def main(filename, size, status_only):
    """Go Main Go."""
    with open(filename) as fh:
        lines = fh.readlines()[::-1]
    # Randomly sample the lines
    lines = random.sample(lines, min(len(lines), size))
    for line in tqdm(lines):
        uri = line.split()[6]
        if uri.endswith("fmt=html"):
            continue
        mreq = httpx.get(
            f"https://mesonet.agron.iastate.edu{uri}", timeout=300
        )
        ans_status = mreq.status_code
        ans_lines = len(mreq.text.split("\n"))
        req = httpx.get(f"http://iem.local{uri}", timeout=300)
        dev_status = req.status_code
        dev_lines = len(req.text.split("\n"))
        if ans_status != dev_status or ans_lines != dev_lines:
            print(f"{uri} {ans_status}->{dev_status} {ans_lines}->{dev_lines}")
            if status_only and ans_status == dev_status:
                continue
            with open("local", "wb") as fh:
                fh.write(req.content)
            with open("mesonet", "wb") as fh:
                fh.write(mreq.content)
            return


if __name__ == "__main__":
    main()
