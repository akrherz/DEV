"""Size Metrics"""

import datetime

import matplotlib.pyplot as plt
import pandas as pd
from pyiem.database import get_dbconn


def get_polygon():
    """Polygon logic"""
    return """
    WITH events as (
        SELECT extract(year from issue) as year, w.wfo, eventid,
        phenomena, ST_Area(ST_Transform(geom, 2163)) / 1000000. as st_area
        from sbw w  WHERE
        phenomena in ('SV', 'TO') and significance = 'W' and status = 'NEW'
        and issue < '2022-01-01'
    )
    SELECT year, count(*), sum(st_area) / 7663941. as area
    from events
    GROUP by year ORDER by year
    """


def get_county():
    """County logic"""
    return """
    WITH events as (
        SELECT extract(year from issue) as year, w.wfo, eventid,
        phenomena, u.area2163 as st_area
        from warnings w JOIN ugcs u on (w.gid = u.gid) WHERE
        phenomena in ('SV', 'TO') and significance = 'W'
        and issue < '2022-01-01'
    )
    SELECT year, count(*), sum(st_area)  / 7663941. as area
    from events
    GROUP by year ORDER by year
    """


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis")
    sql = get_polygon()
    df = pd.read_sql(sql, pgconn, index_col="year")
    print(df)

    (fig, ax) = plt.subplots(1, 1)

    ax.bar(df.index.values - 0.2, df["count"].values, width=0.4, fc="r")
    ax.set_ylabel("Warning Count", color="r")

    y2 = ax.twinx()
    y2.bar(df.index.values + 0.2, df["area"].values, width=0.4, fc="b")
    y2.set_ylabel("Size (Contiguous United States)", color="b")

    p1 = plt.Rectangle((0, 0), 1, 1, fc="r")
    p3 = plt.Rectangle((0, 0), 1, 1, fc="b")
    ax.legend([p1, p3], ["Counts", "Size"], loc=2)
    ax.grid(True)

    ax.set_title("NWS *Polygon* Tornado + Severe Thunderstorm Warnings")
    ax.set_ylim(0, 90000)
    y2.set_ylim(0, 25)
    ax.set_xlim(1985.5, 2021.5)

    fig.text(0.01, 0.01, "Generated %s" % (datetime.date.today(),))
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
