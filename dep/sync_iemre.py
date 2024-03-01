"""A one time sync of recently expanded CLI files to IEMRE.

Necessarily since we copied a current Iowa CLI file to all new places in
the CONUS, which is not all that great for a hot start and it would take
many moons to fix it via daily reprocessing.  This at least gets us ballpark.
"""

import os
from datetime import date

import numpy as np
import requests
from tqdm import tqdm

import pandas as pd
from pyiem.dep import EAST, NORTH, SOUTH, WEST, get_cli_fname
from pyiem.util import convert_value


def process(lon, lat, clifn):
    """Make the replacement."""
    # Collect up the IEMRE data
    dfs = []
    for year in range(2007, 2023):
        req = requests.get(
            f"https://mesonet.agron.iastate.edu/iemre/multiday/{year}-01-01/"
            f"{year}-12-31/{lat}/{lon}/json"
        )
        dfs.append(pd.DataFrame(req.json()["data"]))
    df = (
        pd.concat(dfs)
        .set_index("date")
        .assign(
            daily_precip_mm=(
                lambda df_: convert_value(df_["daily_precip_in"], "in", "mm")
            ),
            highc=(
                lambda df_: convert_value(df_["daily_high_f"], "degF", "degC")
            ),
            lowc=(
                lambda df_: convert_value(df_["daily_low_f"], "degF", "degC")
            ),
        )
    )
    with open(clifn, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    newlines = []
    linenum = 0
    cutoff = date(2022, 6, 22)
    while linenum < len(lines):
        if linenum < 15:
            newlines.append(lines[linenum].strip())
            linenum += 1
            continue
        tokens = lines[linenum].strip().split("\t")
        breakpoints = int(tokens[3])
        valid = date(int(tokens[2]), int(tokens[1]), int(tokens[0]))
        # Skip reader ahead
        linenum += breakpoints + 1
        if valid < cutoff:
            iemre = df.loc[f"{valid:%Y-%m-%d}"]
            precip = iemre["daily_precip_mm"]
            tokens[4] = f"{iemre['highc']:.1f}"
            tokens[5] = f"{iemre['lowc']:.1f}"
            tokens[9] = f"{iemre['lowc']:.1f}"  # HACK
        else:
            precip = 0
        tokens[3] = "0"
        if precip > 0.2:  # mm
            tokens[3] = "2"
        newlines.append("\t".join(tokens))
        if tokens[3] != "0":
            newlines.append(f"0.00 0.00\n23.00 {precip:.2f}")

    # Write!
    with open(clifn, "w", encoding="utf-8") as fh:
        fh.write("\n".join(newlines))


def main():
    """Go Main Go."""
    # Look over our domain at 0.25 degree res
    processed = 0
    progress = tqdm(np.arange(WEST, EAST + 0.25, 0.25))
    for lon in progress:
        for lat in np.arange(SOUTH, NORTH + 0.25, 0.25):
            progress.set_description(f"Tot: {processed}")
            # Don't corrupt our already good files
            if -104 <= lon <= -74 and 35 <= lat <= 49:
                continue
            clifn = get_cli_fname(lon, lat)
            if not os.path.isfile(clifn):
                continue
            process(lon, lat, clifn)
            processed += 1


if __name__ == "__main__":
    main()
