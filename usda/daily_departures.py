"""Daily departures from NASS."""
import calendar
from datetime import date, timedelta

from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt
import numpy as np
from pandas.io.sql import read_sql
import pandas as pd


def main():
    """Go Main Go."""
    pgconn = get_dbconn("coop")
    # Don't consider very latent data
    df = read_sql(
        """
        select year::int as year, unit_desc, week_ending, num_value,
        state_alpha from nass_quickstats
        where commodity_desc = 'SOYBEANS' and statisticcat_desc = 'PROGRESS'
        and unit_desc in ('PCT HARVESTED') and
        state_alpha in ('IA', 'IL') and
        util_practice_desc = 'ALL UTILIZATION PRACTICES'
        and num_value is not null and extract(month from week_ending) > 6
        ORDER by week_ending ASC
    """,
        pgconn,
        index_col=None,
    )
    # Add a 31 Dec value of 100, and a 0
    for year, gdf in (
        df[["year", "week_ending"]].groupby("year").agg([min, max]).iterrows()
    ):
        df = df.append(
            {
                "week_ending": date(year, 7, 1),
                "num_value": 0,
                "year": year,
                "doy": 366,
                "state_alpha": "IA",
                "unit_desc": "PCT HARVESTED",
            },
            ignore_index=True,
        )
        df = df.append(
            {
                "week_ending": gdf.values[0] - timedelta(days=7),
                "num_value": 0,
                "year": year,
                "doy": 366,
                "state_alpha": "IA",
                "unit_desc": "PCT HARVESTED",
            },
            ignore_index=True,
        )
        if year == date.today().year:
            continue
        if gdf.values[1].strftime("%m%d") == "1231":
            continue
        df = df.append(
            {
                "week_ending": date(year, 12, 31),
                "num_value": 100,
                "year": year,
                "doy": 366,
                "state_alpha": "IA",
                "unit_desc": "PCT HARVESTED",
            },
            ignore_index=True,
        )
    df = df.sort_values("week_ending", ascending=True)
    df["week_ending"] = pd.to_datetime(df["week_ending"])
    df = df.set_index("week_ending")
    (fig, ax) = plt.subplots(1, 1)
    ls = {"PCT HARVESTED": "-", "PCT EMERGED": "-."}
    st = {2012: "g", 2019: "k", 2020: "r", 2021: "b"}
    for state in ["IA"]:
        for unit in ["PCT HARVESTED"]:
            df2 = df[(df["unit_desc"] == unit) & (df["state_alpha"] == state)]
            df3 = df2.resample("D").interpolate(method="linear")
            df3["doy"] = pd.to_numeric(df3.index.strftime("%j"))
            avg = (
                df3[(df3["year"] > 2005) & (df3["year"] < 2021)]
                .groupby("doy")
                .mean()
            )
            bins = avg["num_value"].values[183:]
            for year in [2012, 2019, 2020, 2021]:
                obs = df3[df3["year"] == year].set_index("doy")
                obs = obs[obs["num_value"] > 0]
                print(obs.tail(30))
                placement = np.digitize(obs["num_value"], bins) + 183
                data = placement - obs.index.values
                ax.plot(
                    obs.index.values,
                    data,
                    label=f"{year}",
                    linestyle=ls[unit],
                    lw=2,
                    color=st[year],
                )
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(240, 336)
    ax.set_yticks(range(-14, 29, 7))
    ax.grid(True)
    ax.set_ylabel("Estimated Days Ahead of Average Progress")
    ax.set_title(
        "USDA NASS Iowa Soybean Acres Harvested\n"
        "Departure from 2006-2020 Average"
    )
    ax.legend(ncol=1)
    ax.set_xlabel("Daily values linearly interpolated from weekly data")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
