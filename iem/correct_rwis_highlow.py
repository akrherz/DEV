"""We were ingesting the RWIS using UTC days as local day high / lows"""
from __future__ import print_function
import psycopg2
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable

NETWORK = NetworkTable(
    [
        "IL_RWIS",
        "IA_RWIS",
        "AK_RWIS",
        "WV_RWIS",
        "KY_RWIS",
        "NE_RWIS",
        "ND_RWIS",
        "WY_RWIS",
        "ME_RWIS",
        "NH_RWIS",
        "GA_RWIS",
        "MO_RWIS",
        "KS_RWIS",
        "IN_RWIS",
        "MD_RWIS",
        "VA_RWIS",
        "VT_RWIS",
        "WI_RWIS",
        "SD_RWIS",
        "MN_RWIS",
        "CO_RWIS",
        "NV_RWIS",
        "OH_RWIS",
        "DE_RWIS",
        "MI_RWIS",
        "MA_RWIS",
    ]
)


def main():
    """Do Some workflow"""
    iemaccess = psycopg2.connect(
        database="iem", host="localhost", port=5555, user="mesonet"
    )
    rwis = psycopg2.connect(
        database="rwis", host="localhost", port=5555, user="nobody"
    )
    for sid in NETWORK.sts:
        obs = read_sql(
            """
        SELECT date(valid at time zone %s), max(tmpf), min(tmpf)
        from alldata WHERE station = %s GROUP by date ORDER by date ASC
        """,
            rwis,
            params=(NETWORK.sts[sid]["tzname"], sid),
            index_col="date",
        )
        current = read_sql(
            """
        SELECT day, max_tmpf, min_tmpf from summary s JOIN stations t on
        (s.iemid = t.iemid) WHERE t.network = %s and t.id = %s
        ORDER by day ASC
        """,
            iemaccess,
            params=(NETWORK.sts[sid]["network"], sid),
            index_col="day",
        )
        df = obs.join(current)
        idx = (df["max"] != df["max_tmpf"]) | (df["min"] != df["min_tmpf"])
        icursor = iemaccess.cursor()
        updated = 0
        for date, row in df[idx].iterrows():
            table = "summary_%s" % (date.year,)
            # print(("%s High: %s -> %s Low: %s -> %s"
            #        ) % (date, row['max_tmpf'], row['max'],
            #             row['min_tmpf'], row['min']))
            icursor.execute(
                """
            UPDATE """
                + table
                + """ SET max_tmpf = %s, min_tmpf = %s
            WHERE iemid = %s and day = %s
            """,
                (row["max"], row["min"], NETWORK.sts[sid]["iemid"], date),
            )
            updated += 1
        print(
            ("Updated %s rows for %s between %s and %s")
            % (updated, sid, df.index.min(), df.index.max())
        )
        icursor.close()
        iemaccess.commit()


if __name__ == "__main__":
    main()
