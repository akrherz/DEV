"""Request for maps and data of products without SVS updates."""

from pyiem.util import get_sqlalchemy_conn
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot
import pandas as pd


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            """
        WITH data as (
            SELECT wfo, eventid, extract(year from issue) as year,
            max(case when svs is not null then 1 else 0 end) as hit from
            warnings where product_issue > '2021-06-01' and
            product_issue < '2022-06-01' and phenomena = 'TO'
            and significance = 'W' GROUP by wfo, eventid, year
        )
        SELECT wfo, sum(hit) as got_update, count(*) as total_events from data
        GROUP by wfo ORDER by total_events DESC
        """,
            conn,
            index_col="wfo",
        )
    if "JSJ" in df.index and "SJU" not in df.index:
        df.loc["SJU"] = df.loc["JSJ"]

    df["no_update_percent"] = (
        100.0 - df["got_update"] / df["total_events"] * 100.0
    )
    df.to_csv("/tmp/svr_nofls.csv")
    nationwide = (
        (df["total_events"].sum() - df["got_update"].sum())
        / df["total_events"].sum()
        * 100.0
    )
    df["relative"] = df["no_update_percent"] - nationwide

    # NOTE: FFW followup is FFS
    mp = MapPlot(
        sector="nws",
        title="Percent of Tornado Warnings without a SVS Update Issued",
        subtitle=(
            "1 Jun 2021 - 31 May 2022 based on unofficial IEM data. "
            f"Overall: {df['total_events'].sum() - df['got_update'].sum()}/"
            f"{df['total_events'].sum()} {nationwide:.1f}%"
        ),
    )
    cmap = get_cmap("copper_r")
    ramp = range(0, 101, 10)
    mp.fill_cwas(
        df["no_update_percent"],
        bins=ramp,
        cmap=cmap,
        units="Percent",
        ilabel=True,
        lblformat="%.1f",
    )
    mp.postprocess(filename="210601_220531_tor_nosvs.png")


if __name__ == "__main__":
    main()
