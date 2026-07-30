"""Compare with older DEP output."""

import os

import pandas as pd
from dailyerosion.io.dep import read_env
from tqdm import tqdm


def main():
    """Go Main Go."""
    os.chdir("/i/0/env/10230003/1211/")
    progress = tqdm(os.listdir("."))
    frames = []
    for envfn in progress:
        progress.set_description(f"{envfn}")
        frames.append(read_env(envfn).reset_index())

    df = pd.concat(frames)
    total = 0.0
    for dt in pd.date_range("2007/01/01", "2007/12/31"):
        subdf = df[df["date"] == dt]
        if subdf.empty:
            continue
        total += subdf["av_det"].sum() / 135.0
    print(total)


if __name__ == "__main__":
    main()
