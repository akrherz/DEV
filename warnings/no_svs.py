"""Request for maps and data of products without SVS updates."""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            """
        WITH data as (
            SELECT wfo, vtec_year, eventid,
            max(case when status = 'NEW' then 1 else 0 end) as no_svs from
            warnings where product_issue > '2021-01-01' and
            phenomena = 'TO'
            and significance = 'W' GROUP by wfo, eventid, vtec_year
        )
        SELECT wfo, sum(no_svs) as misses, count(*) as total_events from data
        GROUP by wfo ORDER by total_events DESC
        """,
            conn,
            index_col="wfo",
        )
    if "JSJ" in df.index and "SJU" not in df.index:
        df.loc["SJU"] = df.loc["JSJ"]

    df["no_update_percent"] = df["misses"] / df["total_events"] * 100.0
    df.to_csv("/tmp/tor_nosvs.csv")
    nationwide = df["misses"].sum() / df["total_events"].sum() * 100.0
    df["relative"] = df["no_update_percent"] - nationwide

    # NOTE: FFW followup is FFS
    mp = MapPlot(
        sector="nws",
        title="Percent of Tornado Warnings without a SVS Update Issued",
        subtitle=(
            "1 Jan 2021 - 28 Aug 2025 based on unofficial IEM data. "
            f"Overall: {df['misses'].sum()}/"
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
    mp.postprocess(filename="210101_250828_tor_nosvs.png")


if __name__ == "__main__":
    main()
