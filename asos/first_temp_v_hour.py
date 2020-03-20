"""What was the hour of the first fall temp min"""
from __future__ import print_function

from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go"""
    pgconn = get_dbconn("asos")
    df = read_sql(
        """
    WITH mins as (
        SELECT extract(year from valid) as year, min(tmpf) from
        alldata where station = 'DSM' and extract(month from valid) in (8, 9)
        and tmpf is not null GROUP by year),
    agg as (
        SELECT m.year, valid, tmpf::int as t2, m.min
        from alldata a JOIN mins m on
        (extract(year from a.valid) = m.year) WHERE
        a.station = 'DSM' and m.min > a.tmpf
        and extract(month from valid) = 10),
    agg2 as (
        SELECT year, valid, t2,
        row_number() OVER (PARTITION by t2, year ORDER by valid ASC) from agg)

    select valid, year,
    extract(hour from valid + '10 minutes'::interval) as hr,
    t2 from agg2 WHERE row_number = 1
    """,
        pgconn,
        index_col=None,
    )

    (fig, ax) = plt.subplots(1, 1)
    ax.scatter(df["hr"], df["t2"])
    ax.grid(True)
    ax.set_ylabel(r"New Fall Minimum Temperature [$^\circ$F]")
    ax.set_title(
        (
            "October Hour that new Fall Minimum Temperature was Set\n"
            "(DSM) Des Moines Airport (%i-%i)"
        )
        % (df["year"].min(), df["year"].max())
    )
    ax.set_xticks(range(0, 25, 4))
    ax.set_xticklabels(["Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM", "Mid"])
    ax.set_xlabel("Central Standard or Daylight Time")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
