"""Make a map"""

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.geoplot import MapPlot
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def get_data():
    """The data we want and the data we need"""
    pgconn = get_dbconn("coop", user="nobody")
    df = read_sql(
        """
        select year, week_ending, num_value, state_alpha from nass_quickstats
        where commodity_desc = 'CORN' and statisticcat_desc = 'PROGRESS'
        and unit_desc = 'PCT SILKING' and
        util_practice_desc = 'ALL UTILIZATION PRACTICES'
        and num_value is not null
        ORDER by state_alpha, week_ending
    """,
        pgconn,
        index_col=None,
    )
    df["week_ending"] = pd.to_datetime(df["week_ending"])
    data = {}
    for state, gdf in df.groupby("state_alpha"):
        sdf = gdf.copy()
        sdf.set_index("week_ending", inplace=True)
        newdf = sdf.resample("D").interpolate(method="linear")
        y10 = newdf[newdf["year"] > 2007]
        doyavgs = y10.groupby(y10.index.strftime("%m%d")).mean()
        lastdate = pd.Timestamp(newdf.index.values[-1]).to_pydatetime()
        data[state] = {
            "date": lastdate,
            "avg": doyavgs.at[lastdate.strftime("%m%d"), "num_value"],
            "d2017": newdf.at[lastdate, "num_value"],
        }
        print("%s %s" % (state, data[state]))
    return data


def main():
    """Go Main Go"""
    data = get_data()
    mp = MapPlot(
        sector="midwest",
        title="8 July 2018 USDA NASS Corn Progress Percent Silking",
        subtitle=(
            "Top value is 2018 percentage, bottom value is "
            "departure from 2008-2017 avg"
        ),
    )
    data2 = {}
    labels = {}
    for state in data:
        val = data[state]["d2017"] - data[state]["avg"]
        data2[state] = val
        labels[state.encode("utf-8")] = "%i%%\n%s%.1f%%" % (
            data[state]["d2017"],
            "+" if val > 0 else "",
            val,
        )

    print(labels)
    levels = range(-40, 41, 10)
    mp.fill_states(
        data2,
        ilabel=True,
        labels=labels,
        bins=levels,
        cmap=plt.get_cmap("RdBu_r"),
        units="Absolute %",
        labelfontsize=16,
    )
    mp.postprocess(filename="test.png")
    mp.close()


if __name__ == "__main__":
    main()
