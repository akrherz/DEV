"""Request for maps and data of products without SVS updates."""

from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.plot.geoplot import MapPlot
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    dbconn = get_dbconn("postgis")
    df = read_sql(
        """
    WITH data as (
        SELECT wfo, eventid, extract(year from issue) as year,
        max(case when svs is not null then 1 else 0 end) as hit from
        warnings where product_issue > '2008-01-01' and
        product_issue < '2020-01-01' and phenomena = 'FF'
        and significance = 'W' GROUP by wfo, eventid, year
    )
    SELECT wfo, sum(hit) as got_update, count(*) as total_events from data
    GROUP by wfo ORDER by total_events DESC
    """,
        dbconn,
        index_col="wfo",
    )
    if "JSJ" in df.index and "SJU" not in df.index:
        df.loc["SJU"] = df.loc["JSJ"]

    df["no_update_percent"] = (
        100.0 - df["got_update"] / df["total_events"] * 100.0
    )
    df.to_csv("080101_191231_svr_nofls.csv")

    # NOTE: FFW followup is FFS
    mp = MapPlot(
        sector="nws",
        title="Percentage of Flash Flood Warnings without a FFS Update Issued",
        subtitle=(
            "1 Jan 2008 - 31 December 2019" ", based on unofficial data"
        ),
    )
    cmap = plt.get_cmap("copper_r")
    cmap.set_under("white")
    cmap.set_over("black")
    ramp = range(0, 101, 5)
    mp.fill_cwas(
        df["no_update_percent"],
        bins=ramp,
        cmap=cmap,
        units="%",
        ilabel=True,
        lblformat="%.1f",
    )
    mp.postprocess(filename="080101_191231_ffw_nosvs.png")


if __name__ == "__main__":
    main()
