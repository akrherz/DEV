"""
backfill_product_id.py left some things to cleanup/review.

see akrherz/pyIEM#857
"""

from datetime import datetime

import click
import httpx
from sqlalchemy import text
from tqdm import tqdm

import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.nws.product import TextProduct
from pyiem.util import noaaport_text


@click.command()
@click.option("--year", type=int, help="Year to work on...")
def main(year):
    """Go Main Go."""
    # Find a batch of product_ids that need to be run
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(f"""
            select ctid, report, svs, tableoid::regclass as table,
            cardinality(array_remove(string_to_array(svs, '__', ''), NULL))
                 as svscnt, cardinality(product_ids), product_ids, updated
            from warnings_{year} where
            cardinality(array_remove(string_to_array(svs, '__', ''), NULL)) + 1
            != cardinality(product_ids) or
            cardinality(product_ids) = 0
            """),
            conn,
            params=dict(
                sts=datetime(year, 1, 1),
                ets=datetime(year + 1, 1, 1),
            ),
        )
    df["svs"] = df["svs"].fillna("")
    progress = tqdm(df.iterrows(), total=len(df.index))
    pgconn = get_dbconn("postgis")
    for _, row in progress:
        progress.set_description(f"{row['table']} {row['ctid']}")
        product_ids = row["product_ids"]
        answer = row["svscnt"] + 1
        computed = []
        try:
            prod = TextProduct(
                noaaport_text(row["report"]), parse_segments=False
            )
        except Exception as exp:
            print(f"Failed to parse report: {exp}")
            continue
        if abs(prod.valid.year - year) > 1:
            print(f"Skipping {prod.valid} as too far in the future")
            continue
        if prod.afos is None:
            print("Failed to parse report")
            return
        computed.append(prod.get_product_id())
        for svstext in row["svs"].split("__\001"):
            if svstext.strip() == "":
                continue
            svstext = noaaport_text(svstext)
            if len(svstext) < 150:
                print("Skipping short SVS")
                answer -= 1
                continue
            try:
                prod = TextProduct(svstext, parse_segments=False)
            except Exception as exp:
                print(f"Failed to parse SVS: {exp}")
                continue
            # if prod.valid.year != year:
            #    print(f"Skipping {prod.valid}")
            #    continue
            if prod.afos is None:
                print("Failed to parse report")
                return
            computed.append(prod.get_product_id())
        for product_id in computed:
            # Can we get this product_id from the webservice
            url = (
                f"http://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
            )
            try:
                res = httpx.get(url)
                if res.status_code == 502:
                    res = httpx.get(url)
                res.raise_for_status()
            except Exception:
                print(f"{product_id} failed {res.status_code}")
                return
        if len(computed) == answer:
            print(product_ids, computed)
            cursor = pgconn.cursor()
            cursor.execute(
                f"UPDATE {row['table']} SET product_ids = %s WHERE ctid = %s",
                (computed, row["ctid"]),
            )
            cursor.close()
            pgconn.commit()


if __name__ == "__main__":
    main()
