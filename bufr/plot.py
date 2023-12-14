"""plot UA"""

import pandas as pd
from pyiem.plot import figure_axes


def main():
    """Go Main Go."""
    df = pd.read_csv("list", sep="\s+")

    fig, ax = figure_axes(
        title="Omaha 13 Dec 2023 00 UTC Sounding", figsize=(8, 6)
    )
    ax.plot(df["TMPK"] - 273.15, df["HGHT"], label="Temperature")
    ax.plot(df["DWPK"] - 273.15, df["HGHT"], label="Dew Point")
    ax.set_ylim(0, 2000)
    ax.set_ylabel("Geopotential Height [m]")
    ax.set_xlabel("Temperature [C]")
    ax.grid(True)
    ax.legend()
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
