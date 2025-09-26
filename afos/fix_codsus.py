"""CODSUS needs some cleaning.

https://github.com/Unidata/MetPy/issues/3921
https://github.com/Unidata/MetPy/pull/3922
"""

import re
from io import BytesIO

from metpy.io import parse_wpc_surface_bulletin
from pyiem.database import sql_helper, with_sqlalchemy_conn
from sqlalchemy.engine import Connection

ALLOWED_CHARS = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ\r\n ")
"""
        # Does this string have bad characters?
        result = set(row["data"]).difference(ALLOWED_CHARS)
        if result:
            print(result)
            cleaned = row["data"]
            for char in result:
                cleaned = cleaned.replace(char, "")
            bio = BytesIO(cleaned.encode("ascii"))
            try:
                parse_wpc_surface_bulletin(bio, year=2000)
            except Exception:
                print("Double failure")
                continue
            conn.execute(
                sql_helper("
    update {table} SET data = :data where ctid = :ctid
                           ", table=table),
                {"data": cleaned, "ctid": row["ctid"]},
            )
            conn.commit()
"""


@with_sqlalchemy_conn("afos")
def do_table(table: str, conn: Connection | None = None):
    """Go Main Go."""
    res = conn.execute(
        sql_helper(
            """
    select ctid, data from {table} where pil = 'CODSUS' order by entered ASC
                   """,
            table=table,
        )
    )
    for row in res.mappings():
        bio = BytesIO(row["data"].encode("ascii"))
        try:
            parse_wpc_surface_bulletin(bio, year=2000)
        except Exception as exp:
            errmsg = str(exp)
            if "could not convert string" not in errmsg:
                continue
            # dot comes from metpy
            badchars = re.findall(r"[\"']\s*(.*?)\s*[\"']", errmsg)[0].replace(
                ".", ""
            )
            justdigits = re.sub(r"[^0-9]", "", badchars)
            if badchars != "" and badchars in row["data"]:
                print(f"{errmsg} {badchars} -> {justdigits}")
                cleaned = row["data"].replace(badchars, justdigits)
                bio = BytesIO(cleaned.encode("ascii"))
                try:
                    parse_wpc_surface_bulletin(bio, year=2000)
                except Exception:
                    print("Double failure")
                    continue
                conn.execute(
                    sql_helper(
                        "update {table} SET data = :data where ctid = :ctid",
                        table=table,
                    ),
                    {"data": cleaned, "ctid": row["ctid"]},
                )
                conn.commit()


def main():
    """Go Main Go."""
    for year in range(1994, 2000):
        for suffix in ["0106", "0712"]:
            table = f"products_{year}_{suffix}"
            print(f"Processing {table}")
            do_table(table)


if __name__ == "__main__":
    main()
