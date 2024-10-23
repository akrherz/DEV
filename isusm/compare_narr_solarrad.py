"""
Plot a comparison of IEMRE solar rad vs ISUSM
"""

import datetime

import click
import httpx
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.plot import figure
from pyiem.util import get_sqlalchemy_conn
from scipy import stats


def do(station, year):
    """Do as I Say."""
    nt = NetworkTable("ISUSM")
    # Fetch the IEMRE data to get the daily radiation values
    req = httpx.get(
        "http://iem.local/iemre/multiday/"
        f"{year}-01-01/{year}-12-31/{nt.sts[station]['lat']}/"
        f"{nt.sts[station]['lon']}/json"
    )
    iemre = pd.DataFrame(
        req.json()["data"],
        index=pd.date_range(f"{year}-01-01", f"{year}-12-31"),
    )

    # Fetch the ISUAG data
    with get_sqlalchemy_conn("isuag") as conn:
        obs = pd.read_sql(
            """
        select valid, slrkj_tot_qc from sm_daily where station = %s
        and valid >= %s and valid < %s ORDER by valid ASC
            """,
            conn,
            params=(
                station,
                datetime.date(year, 1, 1),
                datetime.date(year + 1, 1, 1),
            ),
            index_col="valid",
        )

    iemre["obs"] = obs["slrkj_tot_qc"] / 1000.0
    iemre["bias"] = iemre["solar_mj"] - iemre["obs"]

    fig = figure(
        title=f"{year} {nt.sts[station]['name']} Daily Solar Radiation Comp",
        figsize=(8, 6),
    )
    ax = fig.add_axes([0.1, 0.1, 0.85, 0.4])
    bias = iemre["bias"].mean()
    h_slope, intercept, h_r_value, _, _ = stats.linregress(
        iemre["obs"].values, iemre["solar_mj"].values
    )
    ax.scatter(iemre["obs"], iemre["solar_mj"], color="tan", edgecolor="None")
    ax.set_ylabel(
        f"IEMRE Grid Extracted mean:{iemre['solar_mj'].mean():.2f} (MJ/d)"
    )
    ax.set_xlabel(f"ISUSM Observation mean:{iemre['obs'].mean():.2f} (MJ/d)")
    ax.plot([0, 40], [0, 40], lw=3, color="r", zorder=2, label="1to1")
    ax.plot(
        [0, 40],
        [0 - bias, 40 - bias],
        lw=3,
        color="k",
        zorder=2,
        label="model bias = %.1f" % (bias,),
    )
    ax.plot(
        [0, 40],
        [intercept, intercept + 40.0 * h_slope],
        color="g",
        lw=3,
        zorder=2,
        label=r"Fit: $R^2 = %.2f$" % (h_r_value**2,),
    )
    ax.legend(loc=2)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid(True)

    ax = fig.add_axes([0.1, 0.55, 0.85, 0.35])
    ax.scatter(iemre.index, iemre["bias"], color="tan", edgecolor="None")
    ax.set_ylabel("IEMRE - ISUSM (MJ/d)")
    ax.grid(True)

    fig.savefig("test.png")


@click.command()
@click.option("--station", type=str)
@click.option("--year", type=int)
def main(station, year):
    """Go Main Go."""
    do(station, year)


if __name__ == "__main__":
    main()
