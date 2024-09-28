"""Stop messing around daryl."""

from datetime import datetime, timedelta, timezone

import click
import httpx
from psycopg import Connection
from sqlalchemy import text

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.lsr import LSR
from pyiem.nws.products.lsr import parser
from pyiem.util import logger, utc

LOG = logger()


def matches(row, lsr: LSR):
    """Yuck."""
    if row["valid"] != lsr.valid:
        return False
    if row["wfo"] != lsr.wfo:
        return False
    if abs(row["lat"] - lsr.geometry.y) > 0.01:
        return False
    if abs(row["lon"] - lsr.geometry.x) > 0.01:
        return False
    print(row["typetext"], lsr.typetext)
    if row["typetext"] != lsr.typetext:
        return False
    print(row["remark"], lsr.remark)
    if pd.isna(row["remark"]) and pd.notna(lsr.remark):
        return False
    if pd.notna(row["remark"]) and pd.isna(lsr.remark):
        return False
    if row["remark"] != lsr.remark:
        return False
    print(row["city"], lsr.city)
    if row["city"] != lsr.city:
        return False
    print(row["county"], lsr.county)
    if row["county"] != lsr.county:
        return False
    print(row["state"], lsr.state)
    if row["state"] != lsr.state:
        return False
    return True


def cross_check(afosdb: Connection, textdf: pd.DataFrame) -> bool:
    """Do some cross checking."""
    problems = False
    for _, row in textdf.iterrows():
        prod = parser(row["data"], utcnow=row["entered"])
        db_product_id = (
            f"{row['entered'].astimezone(timezone.utc):%Y%m%d%H%M}-"
            f"{row['source']}-{row['wmo']}-{row['pil']}"
        )
        if row["bbb"] is not None:
            db_product_id += f"-{row['bbb']}"
        if prod.get_product_id() != db_product_id:
            LOG.info(
                "DB Product_Id: %s updating to: %s",
                db_product_id,
                prod.get_product_id(),
            )
            afosdb.execute(
                text(
                    f"""update {row['table']} SET entered = :entered,
                    source = :source, wmo = :wmo, pil = :pil, bbb = :bbb
                    where ctid = :ctid"""
                ),
                {
                    "entered": prod.valid,
                    "source": prod.source,
                    "wmo": prod.wmo,
                    "pil": prod.afos,
                    "bbb": prod.bbb,
                    "ctid": row["ctid"],
                },
            )
            afosdb.commit()
            problems = True

    return problems


def process_product_id(conn: Connection, product_id: str, df: pd.DataFrame):
    """Do some work."""
    # Step 1, does this product_id exist
    try:
        resp = httpx.get(
            f"https://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}",
            timeout=30,
        )
        if resp.status_code == 200:
            return
    except Exception as exp:
        LOG.info("Failed to fetch %s %s", product_id, exp)
        return
    # Step 2, product does not exist, aggressively look at AFOS database
    prod_valid = datetime.strptime(product_id[:12], "%Y%m%d%H%M").replace(
        tzinfo=timezone.utc
    )
    with get_sqlalchemy_conn("afos") as afosdb:
        problems = True
        while problems:
            textdf = pd.read_sql(
                text(
                    "select *, tableoid::regclass as table, ctid "
                    "from products where pil = :pil and "
                    "entered >= :sts and entered <= :ets order by entered ASC"
                ),
                afosdb,
                params={
                    "pil": f"LSR{df.iloc[0]['wfo']}",
                    "sts": prod_valid - timedelta(hours=1),
                    "ets": prod_valid + timedelta(hours=2),
                },
            )
            if textdf.empty:
                return
            problems = cross_check(afosdb, textdf)
    LOG.info(
        "Product %s not found, loading %s raw lsr text products",
        product_id,
        len(textdf.index),
    )

    # Loop over the text products
    prods = []
    for _, row in textdf.iterrows():
        try:
            prod = parser(row["data"], utcnow=row["entered"])
        except Exception as exp:
            LOG.info(
                "Failed to parse %s %s %s",
                row["entered"],
                row["pil"],
                exp,
            )
            continue
        prods.append(prod)
    # Step 3, loop over the LSRs and see if we can find a match
    fixed = 0
    for prod in prods:
        col = "product_id_summary" if prod.is_summary() else "product_id"
        for _, row in df.iterrows():
            for lsr in prod.lsrs:
                if matches(row, lsr):
                    conn.execute(
                        text(
                            f"UPDATE {row['tablename']} SET {col} = :pid, "
                            "qualifier = :q, unit = :unit where ctid = :ctid"
                        ),
                        {
                            "pid": prod.get_product_id(),
                            "ctid": row["ctid"],
                            "unit": lsr.magnitude_units,
                            "q": lsr.magnitude_qualifier,
                        },
                    )
                    LOG.info(
                        "    Updated %s %s -> %s",
                        col,
                        row[col],
                        prod.get_product_id(),
                    )
                    fixed += 1
    LOG.info("Updated %s rows", fixed)


def do(dt: datetime, conn: Connection):
    """Find things to update."""
    # Step 1, find all the LSRs for this date
    lsrs = pd.read_sql(
        text(
            "select *, ctid, tableoid::regclass as tablename, "
            "ST_x(geom) as lon, ST_y(geom) as lat from lsrs "
            "where valid >= :sts and "
            "valid <= :ets and product_id is not null order by valid asc"
        ),
        conn,
        params={
            "sts": utc(dt.year, dt.month, dt.day),
            "ets": utc(dt.year, dt.month, dt.day, 23, 59),
        },
    )
    LOG.info("Processing %s LSRs for %s", len(lsrs.index), dt)
    # Step 2, group by product_id
    for product_id, gdf in lsrs.groupby("product_id"):
        process_product_id(conn, product_id, gdf)


@click.command()
@click.option("--year", type=int, required=True)
def main(year: int):
    """Go Main Go."""
    for dt in pd.date_range(f"{year}/01/01", f"{year}/12/31"):
        with get_sqlalchemy_conn("postgis") as conn:
            do(dt, conn)
            conn.commit()


if __name__ == "__main__":
    main()
