"""Merge in hourly noaaport files found here:

http://idd.ssec.wisc.edu/native/nwstg/text/
"""

from datetime import datetime, timezone

import click
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.nws.product import TextProduct


@click.command()
@click.option("--valid", type=click.DateTime(), help="UTC valid time to use")
@click.option("--filename", type=click.Path(), help="File to read")
def main(valid: datetime, filename: str):
    """Go Main Go."""
    utcnow = valid.replace(tzinfo=timezone.utc)
    with open(filename, "rb") as fh:
        data = fh.read()
    with get_sqlalchemy_conn("afos") as conn:
        for token in data.decode("ascii", "ignore").split("\003"):
            try:
                tp = TextProduct(
                    token, utcnow=utcnow, ugc_provider={}, parse_segments=False
                )
            except Exception as exp:
                print(exp)
                continue
            if tp.afos is None:
                continue
            part = "0106" if tp.valid.month < 7 else "0712"
            table = f"products_{tp.valid:%Y}_{part}"
            params = {
                "entered": tp.valid,
                "source": tp.source,
                "wmo": tp.wmo,
                "pil": tp.afos,
                "bbb": tp.bbb,
                "data": token,
            }
            res = conn.execute(
                sql_helper(
                    """
    SELECT data from {table} where entered = :entered and
    source = :source and wmo = :wmo and pil = :pil and
    bbb is not distinct from :bbb
                """,
                    table=table,
                ),
                params,
            )
            if res.rowcount > 0:
                continue
            print(tp.get_product_id())
            conn.execute(
                sql_helper(
                    """
            INSERT into {table} (entered, source, wmo, pil, data, bbb)
            VALUES (:entered, :source, :wmo, :pil, :data, :bbb)
            """,
                    table=table,
                ),
                params,
            )
        conn.commit()


if __name__ == "__main__":
    main()
