"""Deduplicate."""

import difflib
import sys

import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import noaaport_text
from tqdm import tqdm


def dotable(date):
    """Go main go"""
    ts1 = date.strftime("%Y-%m-%d 00:00+00")
    ts2 = date.strftime("%Y-%m-%d 23:59+00")
    table = f"products_{date.year}_{'0106' if date.month < 7 else '0712'}"
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    with get_sqlalchemy_conn("afos") as conn:
        df = pd.read_sql(
            f"""
            WITH data as (
                SELECT entered, pil, source, bbb, count(*) from {table}
                WHERE source is not null and wmo is not null
                and pil is not null and entered >= %s and entered <= %s
                GROUP by entered, pil, source)
            select * from data where count > 1
        """,
            conn,
            params=(ts1, ts2),
            index_col=None,
        )
    inserts = 0
    deletes = 0
    considered = 0
    for _, row in tqdm(
        df.iterrows(),
        total=len(df.index),
        desc=date.strftime("%Y%m%d"),
        disable=False,
    ):
        # get text
        cursor.execute(
            f"SELECT data from {table} WHERE source = %s and entered = %s and "
            "pil = %s ORDER by length(data) DESC",
            (row["source"], row["entered"], row["pil"]),
        )
        data = []
        for row2 in cursor:
            text = noaaport_text(row2[0])
            # Do we need to inject the AFOS PIL?
            lines = text.split("\n")
            if lines[3].strip() != row["pil"]:
                if lines[3].strip() == "":
                    lines[3] = f"{row['pil']}\r\r"
                else:
                    lines.insert(3, f"{row['pil']}\r\r")
                if lines[4].strip() != "":
                    lines.insert(4, "\r\r")
                text = "\n".join(lines)
            data.append(text)
        if len(data) < 2:
            # Unsure how we got here, but alas.
            continue
        # Our rectified products should match after the first 11 bytes (LDM)
        # and further yet ignore the WMO header (6+1+4+1+6).
        comp = [x[29:] for x in data]
        hits = 0
        for _i, s in enumerate(difflib.ndiff(comp[0], comp[1])):
            if hits > 11:
                break
            if s[0] == " ":
                continue
            if s[-1] in ["'", "[", "]", "\r", "\n"]:
                continue
            if s[0] == "-":
                # print(u'Delete "{}" from position {}'.format(s[-1], _i))
                hits += 1
            elif s[0] == "+":
                # print(u'Add "{}" to position {}'.format(s[-1], _i))
                hits += 1
        # Compute the number of unique products in this comp
        done = []
        take = []
        for index, x in enumerate(data):
            if comp[index] not in done:
                done.append(comp[index])
                take.append(x)
        # Unique entries matches, nothing to dedup!
        if len(take) == len(data):
            if hits < 10:
                # Take the longest inbound product
                take = [""]
                for x in data:
                    if len(x) > len(take[0]):
                        take[0] = x
            else:
                continue
        considered += 1
        # Delete old entries
        cursor.execute(
            f"DELETE from {table} WHERE source = %s and entered = %s and "
            "pil = %s",
            (row["source"], row["entered"], row["pil"]),
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
                    row["max_wmo"],
                ),
            )
            inserts += 1

    print(f"Deleted {deletes} Inserted {inserts} Considered {considered}")
    cursor.close()
    pgconn.commit()
    pgconn.close()


def main(argv):
    """Do Main"""
    year = int(argv[1])
    for date in pd.date_range(f"{year}/08/26", f"{year}/08/26"):
        dotable(date)


if __name__ == "__main__":
    main(sys.argv)
