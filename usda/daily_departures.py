"""Daily departures from NASS."""
import calendar

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt
import pandas as pd


def main():
    """Go Main Go."""
    pgconn = get_dbconn("coop")
    df = read_sql(
        """
        select year::int as year, unit_desc, week_ending, num_value,
        state_alpha from nass_quickstats
        where commodity_desc = 'CORN' and statisticcat_desc = 'PROGRESS'
        and unit_desc in ('PCT PLANTED', 'PCT EMERGED') and
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
    ls = {"PCT PLANTED": "-", "PCT EMERGED": "-."}
    st = {"IA": "g", "IL": "r"}
    for state in ["IA", "IL"]:
        for unit in ["PCT PLANTED", "PCT EMERGED"]:
            df2 = df[(df["unit_desc"] == unit) & (df["state_alpha"] == state)]
            df3 = df2.resample("D").interpolate(method="linear")
            df3["doy"] = pd.to_numeric(df3.index.strftime("%j"))
            avg = (
                df3[(df3["year"] > 2008) & (df3["year"] < 2019)]
                .groupby("doy")
                .mean()
            )
            d2019 = df3[df3["year"] == 2019].set_index("doy")
            data = d2019["num_value"] - avg["num_value"]
            ax.plot(
                data.index.values,
                data.values,
                label="%s %s" % (state, unit),
                linestyle=ls[unit],
                lw=2,
                color=st[state],
            )
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(90, 155)
    ax.grid(True)
    ax.set_ylabel("Absolute Percentage Departure from 10yr Avg")
    ax.set_title(
        (
            "USDA NASS Corn Acres Planted and Emerged\n"
            "Departure from 2009-2018 Average"
        )
    )
    ax.legend(ncol=1)
    ax.set_xlabel("Daily values linearly interpolated from weekly data")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
