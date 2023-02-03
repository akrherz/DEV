"""Exp plot."""
from datetime import datetime
from itertools import combinations

import pandas as pd
from pyiem.plot.use_agg import plt


def main():
    """Go Main Go."""
    df = pd.read_csv(
        "AEA_Inversion2_MinSI.dat",
        skiprows=[0, 2, 3],
        na_values=["NAN"],
    )
    df["valid"] = pd.to_datetime(df["TIMESTAMP"])
    df = df[df["valid"] > datetime(2021, 7, 8, 10)]

    fig, axes = plt.subplots(3, 1, figsize=(10.24, 7.68))
    ax = axes[0]
    ax.set_title(
        "Ames AEA Farm 8-13 Jul Inversion Station 2 Equal Height Test"
    )
    ax.plot(df["valid"], df["T5_Avg"], label="T107 '5'")
    ax.plot(df["valid"], df["T10_Avg"], label="T107 '10'")
    ax.plot(df["valid"], df["T15_Avg"], label="T107 '15'")
    ax.grid(True)
    ax.set_ylabel("Temperature C")
    ax.legend(ncol=3)

    cols = ["T5_Avg", "T10_Avg", "T15_Avg"]
    df["range"] = df[cols].max(axis=1) - df[cols].min(axis=1)
    # cols = ["T10_Avg", "T15_Avg"]
    # df["range2"] = df[cols].max(axis=1) - df[cols].min(axis=1)
    ax = axes[1]
    ax.plot(df["valid"], df["range"], label="All Three")
    # ax.plot(df["valid"], df["range2"], label="Just T107")
    ax.set_ylabel("Range of Temperature Values C")
    ax.grid(True)
    ax.legend()

    ax = axes[2]
    for one, two in combinations([5, 10, 15], 2):
        df["delta"] = df[f"T{one}_Avg"] - df[f"T{two}_Avg"]
        ax.plot(df["valid"], df["delta"], label=f"{one} - {two}")
        ax.set_ylabel("T107 Difference C")
    ax.grid(True)
    ax.legend()
    fig.savefig("inversion.png")


if __name__ == "__main__":
    main()
