"""Use mesonet.org to attempt to repair a hole."""

import re
from datetime import datetime, timezone

import click
import requests
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.nws.product import TextProduct
from tqdm import tqdm


@click.command()
@click.option("--valid", type=click.DateTime(), help="UTC valid time to use")
def main(valid: datetime):
    """Go Main Go."""
    utcnow = valid.replace(tzinfo=timezone.utc)
    resp = requests.get(
        "https://data.mesonet.org/data/public/"
        f"noaa/text/archive/{utcnow:%Y/%m/%d}/"
    )
    # Find all directory links on that page
    links = re.findall(r'href="([^"]+)"', resp.text)
    progress = tqdm(links)
    ignore = ["HPT/", "WTS/"]
    with get_sqlalchemy_conn("afos") as conn:
        for link in progress:
            if not link.endswith("/") or len(link) != 4 or link in ignore:
                continue
            resp = requests.get(
                "https://data.mesonet.org/data/public/"
                f"noaa/text/archive/{utcnow:%Y/%m/%d}/{link}"
            )
            sublinks = re.findall(r'href="([^"]+)"', resp.text)
            for sublink in sublinks:
                if not sublink.endswith(".txt"):
                    continue
                progress.set_description(sublink)
                resp = requests.get(
                    "https://data.mesonet.org/data/public/"
                    f"noaa/text/archive/{utcnow:%Y/%m/%d}/{link}{sublink}"
                )
                try:
                    tp = TextProduct(
                        resp.text,
                        utcnow=utcnow,
                        ugc_provider={},
                        parse_segments=False,
                    )
                except Exception as exp:
                    print(exp)
                    continue
                if tp.afos is None or tp.afos.startswith(("TST", "CAP")):
                    continue
                part = "0106" if tp.valid.month < 7 else "0712"
                table = f"products_{tp.valid:%Y}_{part}"
                params = {
                    "entered": tp.valid,
                    "source": tp.source,
                    "wmo": tp.wmo,
                    "pil": tp.afos,
                    "bbb": tp.bbb,
                    "data": resp.text,
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
                progress.write(tp.get_product_id())
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
