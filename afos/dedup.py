"""Deduplicate."""
import sys

from tqdm import tqdm
from pyiem.util import noaaport_text, get_dbconn
from pandas.io.sql import read_sql


def dotable(table):
    """Go main go"""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    df = read_sql(
        f"""
        WITH data as (
            SELECT entered, pil, wmo, source, count(*) from {table}
            WHERE source is not null and wmo is not null and pil is not null
            and entered is not null
            GROUP by entered, pil, wmo, source)
        select * from data where count > 1
    """,
        pgconn,
        index_col=None,
    )
    inserts = 0
    deletes = 0
    considered = 0
    for _, row in tqdm(
        df.iterrows(), total=len(df.index), desc=table, disable=False
    ):
        # get text
        cursor.execute(
            f"""
            SELECT data from {table}
            WHERE source = %s and entered = %s and pil = %s and wmo = %s
            ORDER by length(data) DESC
        """,
            (row["source"], row["entered"], row["pil"], row["wmo"]),
        )
        data = []
        for row2 in cursor:
            text = noaaport_text(row2[0])
            data.append(text)
        if len(data) < 2:
            # Unsure how we got here, but alas.
            continue
        # Our rectified products should match after the first 11 bytes (LDM)
        # and further yet ignore the WMO header (6+1+4+1+6).
        comp = [x[29:] for x in data]
        # Compute the number of unique products in this comp
        done = []
        take = []
        for index, x in enumerate(data):
            if comp[index] not in done:
                done.append(comp[index])
                take.append(x)
        # Unique entries matches, nothing to dedup!
        if len(take) == len(data):
            continue
        considered += 1
        # Delete old entries
        cursor.execute(
            f"""
        DELETE from {table}
        WHERE source = %s and entered = %s and pil = %s and wmo = %s
        """,
            (row["source"], row["entered"], row["pil"], row["wmo"]),
        )
        deletes += cursor.rowcount
        for x in take:
            # insert without trailing ^C
            cursor.execute(
                f"""
            INSERT into {table} (data, pil, entered, source, wmo)
            VALUES (%s, %s, %s, %s, %s)
            """,
                (
                    x[:-1],
                    row["pil"],
                    row["entered"],
                    row["source"],
                    row["wmo"],
                ),
            )
            inserts += 1

    print(f"Deleted {deletes} Inserted {inserts} Considered {considered}")
    cursor.close()
    pgconn.commit()
    pgconn.close()


def main(argv):
    """Do Main"""
    for year in range(int(argv[1]), int(argv[2])):
        for col in ["0106", "0712"]:
            table = "products_%s_%s" % (year, col)
            dotable(table)


if __name__ == "__main__":
    main(sys.argv)
