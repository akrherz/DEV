"""SBW Intersection"""

import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    # wfo = argv[1]
    pgconn = get_dbconn("postgis")
    df = read_sql(
        """
        select extract(year from issue)::int as year,
        avg(init_expire - issue) as init_duration,
        avg(expire - issue) as duration from sbw where phenomena = 'TO'
        and status = 'NEW' and
        (expire - issue) < '2 hours'::interval and expire > issue
        GROUP by year ORDER by year
    """,
        pgconn,
        index_col="year",
    )
    (fig, ax) = plt.subplots(1, 1)
    vals = df["init_duration"] / np.timedelta64(1, "s")
    print(vals)
    ax.bar(df.index.values, vals / 60.0, zorder=2, color="b")
    vals = df["duration"] / np.timedelta64(1, "s")
    print(vals)
    ax.bar(df.index.values, vals / 60.0, zorder=3, color="r", width=0.8)
    ax.set_xticks(range(2005, 2021, 5))
    ax.set_ylim(25, 43)
    ax.set_ylabel("2002-2020 Average Warning Duration at Issuance [minutes]")
    ax.set_title("Average NWS Tornado Warning Duration at Issuance")
    fig.text(0.01, 0.01, "@akrherz 24 Sep 2020")
    ax.grid(True)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
