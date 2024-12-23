"""A table of comparables to extremes of 3 Oct 2018."""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable


def main():
    """Go!"""
    nt = NetworkTable("IA_ASOS")
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
        SELECT id, valid, tmpf::int as tmpf, dwpf::int as dwpf,
        sknt from current_log c JOIN stations t
        on (c.iemid = t.iemid) WHERE t.network = 'IA_ASOS' and
        c.valid > 'TODAY' and c.tmpf > 70 ORDER by id ASC
        """,
            conn,
            index_col=None,
        )

    for _, row in df.iterrows():
        with get_sqlalchemy_conn("asos") as conn:
            df2 = pd.read_sql(
                """
                SELECT valid, tmpf, dwpf, sknt from alldata WHERE
                station = %s and valid < '2018-10-03' and tmpf::int >= %s
                and dwpf::int >= %s and sknt >= %s ORDER by valid DESC
            """,
                conn,
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
