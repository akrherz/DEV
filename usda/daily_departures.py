"""Daily departures from NASS."""
import calendar

from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt
from pandas.io.sql import read_sql
import pandas as pd


def main():
    """Go Main Go."""
    pgconn = get_dbconn("coop")
    df = read_sql(
        """
        select year::int as year, unit_desc, week_ending, num_value,
        state_alpha from nass_quickstats
        where commodity_desc = 'SOYBEANS' and statisticcat_desc = 'PROGRESS'
        and unit_desc in ('PCT HARVESTED') and
        state_alpha in ('IA', 'IL') and
        util_practice_desc = 'ALL UTILIZATION PRACTICES'
        and num_value is not null
        ORDER by week_ending ASC
    """,
        pgconn,
        index_col=None,
    )
    df["week_ending"] = pd.to_datetime(df["week_ending"])
    df = df.set_index("week_ending")
    (fig, ax) = plt.subplots(1, 1)
    ls = {"PCT HARVESTED": "-", "PCT EMERGED": "-."}
    st = {2012: "g", 2019: "k", 2020: "r"}
    for state in ["IA"]:
        for unit in ["PCT HARVESTED"]:
            df2 = df[(df["unit_desc"] == unit) & (df["state_alpha"] == state)]
            df3 = df2.resample("D").interpolate(method="linear")
            df3["doy"] = pd.to_numeric(df3.index.strftime("%j"))
            avg = (
                df3[(df3["year"] > 2008) & (df3["year"] < 2020)]
                .groupby("doy")
                .mean()
            )
            for year in [2012, 2019, 2020]:
                d2020 = df3[df3["year"] == year].set_index("doy")
                data = d2020["num_value"] - avg["num_value"]
                ax.plot(
                    data.index.values,
                    data.values,
                    label=f"{year}",
                    linestyle=ls[unit],
                    lw=2,
                    color=st[year],
                )
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(240, 330)
    ax.grid(True)
    ax.set_ylabel("Absolute Percentage Departure from 10yr Avg")
    ax.set_title(
        (
            "USDA NASS Iowa Soybean Acres Harvested\n"
            "Departure from 2009-2019 Average"
        )
    )
    ax.legend(ncol=1)
    ax.set_xlabel("Daily values linearly interpolated from weekly data")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
