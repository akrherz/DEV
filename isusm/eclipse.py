"""Some of the special 15s data from the eclipse."""

import glob

import pandas as pd
from pyiem.plot import figure_axes


def main():
    """Go Main."""
    frames = []
    for fn in glob.glob("/tmp/WestPoint*.dat"):
        obs = pd.read_csv(
            fn,
            skiprows=[0, 2, 3],
            na_values=["NAN", "INF"],
            encoding="ISO-8859-1",
        )
        frames.append(obs)
    df = pd.concat(frames).set_index("TIMESTAMP").sort_index()
    print(df)

    fig, ax = figure_axes(title="Eclipse 15s Data")
    ax.plot(df.index.values, df["SlrW"], label="Wind Speed [m/s]")
    fig.savefig("240409.png")


if __name__ == "__main__":
    main()
