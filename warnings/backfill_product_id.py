"""
Fill out database entries for product_ids and product_id.

see akrherz/pyIEM#857
"""

import time
from datetime import datetime, timedelta, timezone

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.nws.product import TextProduct
from pyiem.util import noaaport_text
from sqlalchemy import text
from tqdm import tqdm


def afos_fix(prod):
    """We have some one-offs, likely...."""
    product_id = prod.get_product_id()
    # 201106022303-KVEF-WWUS85-RFWVEF-CCA
    tokens = product_id.split("-")
    valid = datetime.strptime(tokens[0], "%Y%m%d%H%M").replace(
        tzinfo=timezone.utc
    )
    pgconn, cursor = get_dbconnc("afos")
    rwcursor = pgconn.cursor()
    cursor.execute(
        """
        select ctid, data, tableoid::regclass as table, bbb,
        entered at time zone 'UTC' as entered from products where
        pil = %s and entered > %s and entered < %s and source = %s
        """,
        (
            tokens[3],
            valid - timedelta(minutes=5),
            valid + timedelta(minutes=5),
            tokens[1],
        ),
    )
    if cursor.rowcount == 0:
        print(f"complete failure to find {product_id}, inserting")
        rwcursor.execute(
            "INSERT into products (pil, data, entered, source, wmo, bbb) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (tokens[3], prod.text, valid, tokens[1], prod.wmo, prod.bbb),
        )
        rwcursor.close()
        pgconn.commit()
        return
    found = False
    for row in cursor:
        dbtime = row["entered"].replace(tzinfo=timezone.utc)
        _prod = TextProduct(row["data"], parse_segments=False, utcnow=dbtime)
        if _prod.get_product_id() == product_id:
            found = True
        rwcursor.execute(
            f"UPDATE {row['table']} SET entered = %s, bbb = %s "
            "WHERE ctid = %s",
            (_prod.valid, _prod.bbb, row["ctid"]),
        )
    if not found:
        print(f"Found {cursor.rowcount} row, no match {product_id}, inserting")
        rwcursor.execute(
            "INSERT into products (pil, data, entered, source, wmo, bbb) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (tokens[3], prod.text, valid, tokens[1], prod.wmo, prod.bbb),
        )

    rwcursor.close()
    pgconn.commit()


@click.command()
@click.option("--year", type=int, help="Year to work on...")
@click.option("--chunksize", default=1000, help="Chunksize")
def main(year, chunksize):
    """Go Main Go."""
    # Find a batch of product_ids that need to be run
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text("""
            select ctid, report, svs, tableoid::regclass as table, wfo,
            updated at time zone 'UTC' as updated,
            issue at time zone 'UTC' as issued
            from warnings where
            cardinality(product_ids) = 0 and report is not null
            and issue > :sts and issue < :ets
            and phenomena = 'FF'
            ORDER by wfo asc, issue asc
            LIMIT :chunksize
            """),
            conn,
            params=dict(
                sts=datetime(year, 1, 1),
                ets=datetime(year + 1, 1, 1),
                chunksize=chunksize,
            ),
        )
    df["svs"] = df["svs"].fillna("")
    pgconn, cursor = get_dbconnc("postgis")
    progress = tqdm(df.iterrows(), total=len(df.index))
    for _, row in progress:
        updated = row["updated"].replace(tzinfo=timezone.utc)
        issued = row["issued"].replace(tzinfo=timezone.utc)
        progress.set_description(f"{row['wfo']} {row['ctid']}")
        report = noaaport_text(row["report"])
        prod = TextProduct(report, parse_segments=False, utcnow=issued)
        if prod.afos is None:
            prod.afos = f"FFW{prod.source[1:]}"
        products = [prod]
        for svstext in row["svs"].split("__"):
            if svstext.strip() == "":
                continue
            svstext = noaaport_text(svstext)
            try:
                prod = TextProduct(
                    svstext, parse_segments=False, utcnow=updated
                )
                # if prod.afos is None:
                #    prod.afos = f"FFS{prod.source[1:]}"
            except Exception as exp:
                print(f"Failed to parse SVS {exp}")
                continue
            products.append(prod)
        trouble = []
        for prod in products:
            # Can we get this product_id from the webservice
            product_id = prod.get_product_id()
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
                trouble.append(prod)
        if trouble:
            list(map(afos_fix, trouble))
            continue
        cursor.execute(
            f"UPDATE {row['table']} SET product_ids = %s WHERE ctid = %s",
            ([x.get_product_id() for x in products], row["ctid"]),
        )
    cursor.close()
    pgconn.commit()
    if len(df.index) < chunksize:
        print("We likely ran dry, sleeping")
        time.sleep(600)


if __name__ == "__main__":
    main()
