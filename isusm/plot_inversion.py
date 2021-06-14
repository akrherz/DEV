"""Exp plot."""

import pandas as pd
from pyiem.plot.use_agg import plt


def main():
    """Go Main Go."""
    df = pd.read_csv("AEA_Inversion_MinSI.dat", skiprows=[0, 2, 3])
    df["valid"] = pd.to_datetime(df["TIMESTAMP"])

    fig, axes = plt.subplots(3, 1, figsize=(10.24, 7.68))
    ax = axes[0]
    ax.set_title(
        "Ames AEA Farm 8-14 June 2021 Inversion Station Equal Height Test"
    )
    ax.plot(df["valid"], df["T5_Avg"], label="CS215 '5'")
    ax.plot(df["valid"], df["T10_Avg"], label="T107 '10'")
    ax.plot(df["valid"], df["T15_Avg"], label="T107 '15'")
    ax.grid(True)
    ax.set_ylabel("Temperature C")
    ax.legend(ncol=3)

    cols = ["T5_Avg", "T10_Avg", "T15_Avg"]
    df["range"] = df[cols].max(axis=1) - df[cols].min(axis=1)
    cols = ["T10_Avg", "T15_Avg"]
    df["range2"] = df[cols].max(axis=1) - df[cols].min(axis=1)
    ax = axes[1]
    ax.plot(df["valid"], df["range"], label="All Three")
    ax.plot(df["valid"], df["range2"], label="Just T107")
    ax.set_ylabel("Range of Temperature Values C")
    ax.grid(True)
    ax.legend()

    df["delta"] = df["T5_Avg"] - df[["T10_Avg", "T15_Avg"]].mean(axis=1)
    ax = axes[2]
    ax.plot(df["valid"], df["delta"], label="All Three")
    ax.set_ylabel("CS215 minus T107 Average C")
    ax.grid(True)
    ax.legend()

    fig.savefig("inversion.png")


if __name__ == "__main__":
    main()
