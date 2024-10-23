"""Upscale Daily Erosion Project (DEP) to SWAT HUC14."""

import sys
from datetime import datetime, timedelta

import geopandas as gpd
import httpx
import numpy as np
import pandas as pd
from tqdm import tqdm


def main():
    """Upscale."""
    dfs = []
    for i in range(1, 4):
        dfs.append(gpd.read_file(f"{i}.json"))
    df = gpd.GeoDataFrame(pd.concat(dfs))
    progress = tqdm(df.iterrows(), total=len(df.index))
    for _, row in progress:
        huc14 = row["name"]
        progress.set_description(huc14)
        (x, y) = row["geometry"].geoms[0].exterior.coords[0]
        req = httpx.get(
            "https://mesonet-dep.agron.iastate.edu/dl/climatefile.py?"
            f"lat={y:.4f}&lon={x:.4f}"
        )
        if req.status_code != 200:
            print(f"Failed {huc14}")
            continue
        lines = req.text.split("\n")
        with open(f"precipitation/{huc14}.txt", "w") as fh:
            fh.write("20070101, 60, precipitation\n")
            linenum = 15
            now = datetime(2007, 1, 1)
            while linenum < (len(lines) - 1):
                now += timedelta(days=1)
                if now.year == 2024:
                    break
                bbcnt = int(lines[linenum].split()[3])
                if bbcnt == 0:
                    fh.write("0.0\n" * 24)
                else:
                    times = []
                    accum = []
                    for _ in range(bbcnt):
                        linenum += 1
                        tokens = lines[linenum].split()
                        times.append(float(tokens[0]))
                        accum.append(float(tokens[1]))
                    bpdf = (
                        pd.DataFrame({"accum": accum}, index=times)
                        .reindex(np.arange(0, 24, 0.01), method="ffill")
                        .fillna(0)
                    )
                    vals = bpdf.iloc[99:2400:100]["accum"].values
                    starts = [0] + vals.tolist()[:-1]
                    deltas = vals - starts
                    if np.min(deltas) < 0:
                        print(f"Negative delta found for {huc14}")
                        print(vals, starts, deltas)
                        sys.exit()
                    for val in deltas:
                        fh.write(f"{val:.2f}\n")

                linenum += 1


if __name__ == "__main__":
    main()
