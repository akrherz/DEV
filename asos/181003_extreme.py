"""A table of comparables to extremes of 3 Oct 2018."""

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go!"""
    nt = NetworkTable("IA_ASOS")
    pgconn = get_dbconn("iem")
    df = read_sql(
        """
    SELECT id, valid, tmpf::int as tmpf, dwpf::int as dwpf,
    sknt from current_log c JOIN stations t
    on (c.iemid = t.iemid) WHERE t.network = 'IA_ASOS' and
    c.valid > 'TODAY' and c.tmpf > 70 ORDER by id ASC
    """,
        pgconn,
        index_col=None,
    )

    pgconn = get_dbconn("asos")
    for _, row in df.iterrows():
        df2 = read_sql(
            """
            SELECT valid, tmpf, dwpf, sknt from alldata WHERE station = %s
            and valid < '2018-10-03' and tmpf::int >= %s and dwpf::int >= %s
            and sknt >= %s ORDER by valid DESC
        """,
            pgconn,
            params=(row["id"], row["tmpf"], row["dwpf"], row["sknt"]),
            index_col=None,
        )
        if len(df2.index) > 5:
            continue
        lastdate = None
        if not df2.empty:
            lastdate = df2.iloc[0]["valid"].date()
        print(
            ("%s,%s,%s,%s,%.0f,%s,%s,%s")
            % (
                row["id"],
                row["valid"],
                row["tmpf"],
                row["dwpf"],
                row["sknt"],
                len(df2.index),
                lastdate,
                nt.sts[row["id"]]["archive_begin"].year,
            )
        )


if __name__ == "__main__":
    main()
