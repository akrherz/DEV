"""A corn planting daily feature"""

import numpy as np

import matplotlib.font_manager
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    colors = ["red", "black", "green", "teal", "purple", "blue"]
    fig, ax = plt.subplots(2, 1, figsize=(8, 6.4))

    pgconn = get_dbconn("coop")
    df = read_sql(
        """
        select year, week_ending, num_value, state_alpha from nass_quickstats
        where commodity_desc = 'CORN' and statisticcat_desc = 'PROGRESS'
        and unit_desc = 'PCT PLANTED' and
        util_practice_desc = 'ALL UTILIZATION PRACTICES'
        and num_value is not null and state_alpha = 'IA'
        ORDER by state_alpha, week_ending
    """,
        pgconn,
        index_col=None,
    )
    df["week_ending"] = pd.to_datetime(df["week_ending"])
    df["doy"] = pd.to_numeric(df["week_ending"].dt.strftime("%j"))
    ldiff = []
    highyears = [1993, 2018, 2012, 2010, 2017, 1991]
    sx = []
    sy = []
    for year, gdf in df.groupby("year"):
        y = gdf["num_value"].values
        deltas = (y[1:] - y[:-1]).tolist()
        maxval = np.max(deltas)
        ldiff.append(maxval)
        sx.append(gdf.iloc[deltas.index(maxval) + 1]["doy"])
        sy.append(y[deltas.index(maxval) + 1])
        ax[0].plot(
            gdf["doy"],
            y,
            lw=3 if year in highyears else 1,
            color="tan" if year not in highyears else colors.pop(),
            label=str(year) if year in highyears else None,
            zorder=3 if year in highyears else 1,
        )
    ax[0].scatter(sx, sy, c="brown", s=30, zorder=4)
    ax[0].set_xlabel(
        (
            "dots represent end of week with "
            "largest yearly planting percentage"
        )
    )
    prop = matplotlib.font_manager.FontProperties(size=12)

    ax[0].legend(ncol=2, loc=4, prop=prop)
    ax[0].set_xticks(
        [91, 105, 121, 135, 152, 166, 182, 213, 244, 274, 305, 335, 365]
    )
    ax[0].set_xticklabels(
        (
            "Apr 1",
            "Apr 15",
            "May 1",
            "May 15",
            "Jun 1",
            "Jun 15",
            "Jul 1",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        )
    )
    ax[0].set_xlim(90, 170)
    ax[0].set_yticks(range(0, 101, 25))
    ax[0].grid(True)
    ax[0].set_title(
        (
            "USDA Weekly Crop Progress Report (1979-2018)\n"
            "Iowa Corn Planting Progress (6 years highlighted)"
        )
    )
    ax[0].set_ylabel("Percent Planted [%]")

    ax[1].bar(np.arange(1979, 2019), ldiff)
    ax[1].set_xlim(1978.5, 2018.5)
    ax[1].set_ylabel("Max Weekly Change [%]")
    ax[1].grid(True)
    ax[1].set_xlabel("valid thru week ending 29 April 2018")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
