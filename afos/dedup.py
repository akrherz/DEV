"""Deduplicate."""

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
    hits = 0
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
        comp = [x[11:] for x in data]
        if comp.count(comp[0]) != len(comp):
            continue
        hits += 1
        # delete old entries
        cursor.execute(
            f"""
        DELETE from {table}
        WHERE source = %s and entered = %s and pil = %s and wmo = %s
        """,
            (row["source"], row["entered"], row["pil"], row["wmo"]),
        )
        # insert without trailing ^C
        cursor.execute(
            f"""
        INSERT into {table} (data, pil, entered, source, wmo)
        VALUES (%s, %s, %s, %s, %s)
        """,
            (
                data[0][:-1],
                row["pil"],
                row["entered"],
                row["source"],
                row["wmo"],
            ),
        )

    print("%s rows were updated..." % (hits,))
    cursor.close()
    pgconn.commit()
    pgconn.close()


def main():
    """Do Main"""
    for year in range(2003, 2004):
        for col in ["0106", "0712"]:
            table = "products_%s_%s" % (year, col)
            dotable(table)


if __name__ == "__main__":
    main()
