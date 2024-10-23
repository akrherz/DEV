"""Pre-2002 sbw database doesn't have much for polygons, we can fix that!"""

import click
import geopandas as gpd
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.nws.product import TextProduct
from pyiem.util import logger
from sqlalchemy import text
from tqdm import tqdm

LOG = logger()


def cull_product_id(year, product_id):
    """Update the database to remove this product_id."""
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text(
                """
            update warnings SET product_ids = '{}' WHERE vtec_year = :year
            and product_ids[1] = :pid
        """
            ),
            {"year": year, "pid": product_id},
        )
        if res.rowcount == 0:
            LOG.info("Failed to cull %s", product_id)
        conn.commit()


def insert(cursor, year, row, prod: TextProduct):
    """Add sbw row, maybe."""
    # do we already have this?
    cursor.execute(
        """
        SELECT eventid, st_area(geom), ctid from sbw WHERE
        vtec_year = %s and wfo = %s and 
        eventid = %s and phenomena = %s and significance = %s and
        status = 'NEW' and product_id = %s order by st_area(geom) asc
    """,
        (
            year,
            row["wfo"],
            row["eventid"],
            row["phenomena"],
            row["significance"],
            row["product_id"],
        ),
    )
    if cursor.rowcount > 0:
        currentrow = cursor.fetchone()
        if prod.segments[0].sbw.area - currentrow["st_area"] > 0.01:
            LOG.info(
                "Updating polygon %s -> %s",
                currentrow["st_area"],
                prod.segments[0].sbw.area,
            )
            cursor.execute(
                """
                UPDATE sbw SET geom = %s WHERE ctid = %s and vtec_year = %s
            """,
                (prod.segments[0].giswkt, currentrow["ctid"], year),
            )
            return
        LOG.debug(
            "Already have %s %s %s",
            row["wfo"],
            row["phenomena"],
            row["eventid"],
        )
        return

    cursor.execute(
        """
        insert into sbw(wfo, eventid, significance, phenomena, status, issue,
        init_expire, expire, polygon_begin, polygon_end, updated, is_emergency,
        is_pds, geom, product_id, vtec_year, product_signature) VALUES(
        %s, %s, %s, %s, 'NEW', %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s)
        """,
        (
            row["wfo"],
            row["eventid"],
            row["significance"],
            row["phenomena"],
            row["issue"],
            row["expire"],
            row["expire"],
            row["issue"],
            row["expire"],
            row["issue"],
            row["is_emergency"],
            row["is_pds"],
            prod.segments[0].giswkt,
            row["product_id"],
            year,
            prod.get_signature(),
        ),
    )


@click.command()
@click.option("--year", type=int, help="Year to process")
def main(year):
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as pgconn:
        cwas = gpd.read_postgis(
            text(
                "select case when wfo = 'SJU' then 'JSJ' else wfo end as wfo, "
                "the_geom, st_xmin(the_geom) as west, "
                "st_xmax(the_geom) as east, st_ymin(the_geom) as south, "
                "st_ymax(the_geom) as north from cwa"
            ),
            pgconn,
            geom_col="the_geom",
            index_col="wfo",
        )
        warnings = pd.read_sql(
            text(
                """
            select distinct wfo, phenomena, significance, eventid, updated,
            issue, expire, is_emergency, is_pds,
            product_ids[1] as product_id from warnings WHERE vtec_year = :year
            and cardinality(product_ids) > 0
            order by wfo, phenomena, significance, eventid
        """
            ),
            pgconn,
            params={"year": year},
        )
    LOG.info("Found %s rows to process", len(warnings.index))
    pgconn, cursor = get_dbconnc("postgis")

    updates = 0
    for _, row in tqdm(warnings.iterrows(), total=len(warnings.index)):
        req = httpx.get(
            "https://mesonet.agron.iastate.edu/api/1/nwstext"
            f"/{row['product_id']}"
        )
        if req.status_code == 404:
            LOG.info("404 for %s, culling", row["product_id"])
            cull_product_id(year, row["product_id"])
            continue
        try:
            prod = TextProduct(req.text, utcnow=row["updated"])
        except Exception as exp:
            LOG.info("Failed to parse %s %s", row["product_id"], exp)
            continue
        if not prod.segments or prod.segments[0].sbw is None:
            continue
        poly = prod.segments[0].sbw
        # Ensure the polygon is not wildly outside of the CWA
        if not cwas.loc[[row["wfo"]]].intersects(poly).any():
            LOG.info(
                "Fails to intersect %s %s %s",
                row["wfo"],
                row["phenomena"],
                row["product_id"],
            )
            continue
        # Ensure that the polygon is within 1 degree of the CWA extent
        cwa = cwas.loc[[row["wfo"]]]
        if (
            poly.bounds[0] < cwa["west"].values[0] - 1
            or poly.bounds[2] > cwa["east"].values[0] + 1
            or poly.bounds[1] < cwa["south"].values[0] - 1
            or poly.bounds[3] > cwa["north"].values[0] + 1
        ):
            LOG.info(
                "Fails to be within 1 degree %s %s %s",
                row["wfo"],
                row["phenomena"],
                row["product_id"],
            )
            continue

        insert(cursor, year, row, prod)
        updates += 1
        if updates % 100 == 0:
            cursor.close()
            pgconn.commit()
            cursor = pgconn.cursor()
    LOG.info("Added %s rows", updates)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
