"""Explore a plot type with how flowpath erosion changes with tillage."""
import glob
import os

import click
from pydep.io.wepp import read_env
from tqdm import tqdm

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure

# pasture, 1, 1.5, 2, 3, 4, 5, 6
SCENARIOS = [165, 157, 164, 158, 159, 160, 161, 162]


def compute(huc12):
    """Compute things."""
    with get_sqlalchemy_conn("idep") as conn:
        fpdf = pd.read_sql(
            "select fpath, real_length, bulk_slope from flowpaths "
            "where huc_12 = %s and scenario = 0",
            conn,
            params=(huc12,),
            index_col="fpath",
        )
    rows = []
    progress = tqdm(
        SCENARIOS
        + [
            0,
        ]
    )
    for scenario in progress:
        progress.set_description(str(scenario))
        dirpath = f"/mnt/depoffload/2/{scenario}/env/{huc12[:8]}/{huc12[8:]}/"
        for fn in glob.glob(f"{dirpath}/*.env"):
            env = read_env(fn)
            fpath = int(os.path.basename(fn).split(".")[0].split("_")[1])
            env["delivery"] = env["sed_del"] / fpdf.at[fpath, "real_length"]
            # trim off 2024
            env = env[env["year"] < 2024]
            rows.append(
                {
                    "scenario": scenario,
                    "fpath": fpath,
                    "delivery": env["delivery"].sum() * 4.463 / 17.0,
                    "detachment": env["av_det"].sum() * 4.463 / 17.0,
                    "bulk_slope": fpdf.at[fpath, "bulk_slope"],
                }
            )
    pd.DataFrame(rows).to_csv(f"scenario_tracks_{huc12}.csv", index=False)


@click.command()
@click.option("--huc12", help="HUC12 to plot.")
def main(huc12):
    """Go Main."""
    fn = f"scenario_tracks_{huc12}.csv"
    if not os.path.isfile(fn):
        compute(huc12)
    dfall = pd.read_csv(fn)
    slope_classes = [0.0, 0.02, 0.02, 0.04, 0.06, 0.1, 0.12, 1.0]
    prod = dfall[dfall["scenario"] == 0].set_index("fpath")
    df = dfall[dfall["scenario"] != 0]

    fig = figure(
        title=(
            f"HUC12 {huc12} Baseline Delivery: "
            f"{prod['delivery'].mean():.2f} [t/a/yr]"
        ),
        subtitle=(
            f"Each line is a flowpath(n={len(prod.index)}), "
            "colored by slope class"
        ),
        logo="dep",
        figsize=(8, 6),
    )
    ax = fig.add_axes([0.13, 0.1, 0.5, 0.8])
    colors = [
        "tan",
        "lightgreen",
        "green",
        "blue",
        "purple",
        "orange",
        "red",
    ]
    for i, sc in enumerate(slope_classes[:-1]):
        df2 = df[
            (df["bulk_slope"] > sc) & (df["bulk_slope"] < slope_classes[i + 1])
        ]
        label = False
        for fpath, gdf in df2.groupby("fpath"):
            ax.plot(
                gdf["delivery"] - prod.at[fpath, "delivery"],
                range(len(gdf["delivery"])),
                color=colors[i],
                label=None
                if label
                else (
                    f"{i+1}: {sc * 100:.0f}-{slope_classes[i + 1] * 100:.0f}%"
                ),
            )
            label = True

    ax.set_xlabel(
        "Hillslope Soil Delivery Change over Flowpath Baseline [t/a/yr]"
    )
    ax.axvline(0, color="k", lw=2)
    ax.set_yticks(range(-1, len(SCENARIOS)))
    ax.set_yticklabels(
        [
            "Baseline",
            "Pasture",
            "No Till",
            "Very High\nMulch\n(no Chisel)",
            "Very High\nMulch",
            "High\nMulch",
            "Medium\nMulch",
            "Low\nMulch",
            "Moldboard\nPlow",
        ]
    )
    ax.legend(title="Slope Class")
    ax.grid()
    ax.set_ylim(bottom=-1.5)

    ax2 = fig.add_axes([0.64, 0.1, 0.25, 0.8])
    for i, scenario in enumerate(
        [
            0,
        ]
        + SCENARIOS
    ):
        df2 = dfall[dfall["scenario"] == scenario]
        # create a boxplot for this scenario
        ax2.boxplot(
            df2["delivery"].values,
            notch=True,
            positions=[i - 1],
            widths=0.5,
            showfliers=False,
            whis=[5, 95],
            vert=False,
        )
        # Place text at the far right with the mean value shown
        ax2.annotate(
            f"{df2['delivery'].mean():.2f}",
            xy=(1.02, i - 1),
            ha="left",
            va="center",
            xycoords=("axes fraction", "data"),
        )
    ax2.annotate(
        "Mean\nDelivery\n[t/a/yr]",
        xy=(1.02, 0),
        ha="left",
        va="top",
        xycoords=("axes fraction", "axes fraction"),
    )
    ax2.set_yticks([])
    ax2.set_xlabel("Delivery [t/a/yr]")
    ax2.grid()
    ax2.set_ylim(*ax.get_ylim())

    fig.savefig("/tmp/test.png")


if __name__ == "__main__":
    main()
