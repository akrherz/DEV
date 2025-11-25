"""Utility script to take the 4km grid and 5x it to fill the 800m grid."""

import shutil
import subprocess

import click
import numpy as np
from pyiem.util import logger, ncopen
from tqdm import tqdm

LOG = logger()


@click.command()
@click.option("--year", type=int, required=True, help="Year to process")
def main(year: int):
    """Go Main Go."""
    ncfn = f"/mesonet/data/prism/{year}_daily.nc"
    LOG.info("Moving %s to orig", ncfn)
    shutil.move(ncfn, f"{ncfn}.orig")

    LOG.info("Creating new file")
    subprocess.call(
        [
            "python",
            "init_daily.py",
            "--year",
            f"{year}",
        ]
    )

    # Fill out the grid
    with ncopen(f"{ncfn}.orig") as ncin, ncopen(ncfn, "a") as ncout:
        for ncvar in ["ppt", "tmax", "tmin"]:
            LOG.info("Filling out %s", ncvar)
            progress = tqdm(range(ncout.dimensions["time"].size))
            progress.set_description(f"Processing {ncvar}")
            for tidx in progress:
                # Get the 4km grid
                data = ncin.variables[ncvar][tidx]
                # Fill out the 800m grid
                ncout.variables[ncvar][tidx] = np.kron(data, np.ones((5, 5)))


if __name__ == "__main__":
    main()
