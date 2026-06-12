"""Explore some theories about mean/median flowpath results."""

from pathlib import Path

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure
from tqdm import tqdm

YEARS = 20


def get_data():
    """Generate the dataset."""
    with get_sqlalchemy_conn("idep") as conn:
        huc12s = pd.read_sql(
            sql_helper("SELECT huc_12 from huc12 where scenario = 0"),
            conn,
        )
    results = []
    progress = tqdm(huc12s["huc_12"].values)
    for huc12 in progress:
        fn = Path(f"/i/0/ofe/{huc12[:8]}/{huc12[8:]}/fpresults_{huc12}.csv")
        fpresults = pd.read_csv(fn)
        # One off capping
        # fpresults = fpresults[fpresults["delivery[t/a/yr]"] > 0.01]
        stats = fpresults["delivery[t/a/yr]"].describe()
        results.append(
            {
                "mean": stats["mean"],
                "median": stats["50%"],
                "huc12": huc12,
                # Read: close to zero
                "percent_zeros": (fpresults["delivery[t/a/yr]"] < 0.01).mean()
                * 100,
                "maxval": stats["max"],
                "tail_distance": stats["max"] - stats["50%"],
                "stddev": stats["std"],
                "count": stats["count"],
            }
        )

    return pd.DataFrame(results)


def main():
    """Go Main Go."""
    csvfn = Path("/tmp/tmp.csv")
    if not csvfn.exists():
        resultdf = get_data()
        resultdf.to_csv(csvfn, index=False)
    resultdf = pd.read_csv(csvfn)
    # Quorum
    quorum = 30
    resultdf = resultdf[resultdf["count"] >= quorum]
    resultdf["ratio"] = resultdf["median"] / resultdf["mean"]

    fig = figure(
        title="Median vs Mean Delivery [T/a/yr]",
        subtitle=(
            f"[2007-2025] {len(resultdf)} HUC12s having {quorum}+ flowpaths"
        ),
        logo="dep",
        figsize=(12.90, 8.60),  # 3x2 grid
    )
    ((ax2, ax4, ax6), (ax, ax3, ax5)) = fig.subplots(
        2, 3, sharex=False, sharey=False
    )

    ax.scatter(resultdf["mean"], resultdf["median"], s=10, color="r")
    ax.set_xlabel("Mean Delivery T/a/yr")
    ax.set_ylabel("Median Delivery T/a/yr")
    ax.grid(True)

    # Ensure x,y axes are the same scale
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 15)

    # Plot x=y
    ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", color="k", label="x=y")

    # Plot a Fit line
    m, b = np.polyfit(resultdf["mean"], resultdf["median"], 1)
    ax.plot(
        resultdf["mean"],
        m * resultdf["mean"] + b,
        color="k",
        label="Linear Fit",
    )

    ax.legend(loc="upper left", fontsize=10, ncol=1)

    # ---------------------------------------------------------
    # Plot ratio by mean value
    ax2.scatter(resultdf["mean"], resultdf["ratio"], s=10, color="b")
    ax2.set_xlim(*ax.get_xlim())
    ax2.grid(True)
    ax2.set_xlabel("Mean Delivery T/a/yr")
    ax2.set_ylabel("Median/Mean Delivery")

    y = []
    x = []
    for ratio in np.arange(0, 1.01, 0.05):
        subset = resultdf[
            (resultdf["ratio"] >= ratio) & (resultdf["ratio"] < ratio + 0.05)
        ]
        if len(subset) > 0:
            y.append(ratio)
            x.append(subset["mean"].mean())

    ax2.plot(x, y, color="k", lw=3, label="Partitioned Fit")
    ax2.legend(loc="upper right", fontsize=10, ncol=1)
    ax2.set_ylim(-0.05)

    # ---------------------------------------------------------
    # Plot % zeros by mean value
    ax3.scatter(resultdf["mean"], resultdf["percent_zeros"], s=10, color="g")
    ax3.set_xlim(*ax.get_xlim())
    ax3.set_ylim(-5, 105)
    ax3.grid(True)
    ax3.set_xlabel("Mean Delivery T/a/yr")
    ax3.set_ylabel("% of Flowpaths with Delivery < 0.01 T/a/yr")

    # ----------------------------------------------------------
    # Plot % zeros by ratio
    ax4.scatter(resultdf["percent_zeros"], resultdf["ratio"], s=10, color="m")
    ax4.set_ylim(*ax2.get_ylim())
    ax4.set_xlim(0, 100)
    ax4.grid(True)
    ax4.set_ylabel("Median/Mean Delivery")
    ax4.set_xlabel("% of Flowpaths with Delivery < 0.01 T/a/yr")

    y = []
    x = []
    for pp in np.arange(0, 101, 5):
        subset = resultdf[
            (resultdf["percent_zeros"] >= pp)
            & (resultdf["percent_zeros"] < pp + 5)
        ]
        if len(subset) > 3:
            x.append(pp)
            y.append(subset["ratio"].mean())

    ax4.plot(x, y, color="k", lw=3, label="Partitioned Fit")
    ax4.legend(loc="upper right", fontsize=10, ncol=1)

    # -----------------------------------
    # Plot tail distance by ratio
    ax6.scatter(resultdf["tail_distance"], resultdf["ratio"], s=10, color="c")
    ax6.set_ylabel("Median/Mean Delivery")
    ax6.set_xlabel("Tail Distance (Max - Median) T/a/yr")
    ax6.grid(True)
    ax6.set_ylim(*ax4.get_ylim())
    ax6.set_xlim(0, 300)

    # ----------------------------------------
    # Plot tail distance normalized by std
    ax5.scatter(
        resultdf["tail_distance"] / resultdf["stddev"],
        resultdf["ratio"],
        s=10,
        color="orange",
    )
    ax5.set_ylabel("Median/Mean Delivery")
    ax5.set_xlabel("Tail Distance / Std Dev")
    ax5.grid(True)
    ax5.set_ylim(*ax4.get_ylim())
    ax5.set_xlim(0, 20)

    fig.savefig("mean_vs_median.png")


if __name__ == "__main__":
    main()
