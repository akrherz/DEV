"""Fix the SIGMET archive..."""

import sys

# third party
import geopandas as gpd
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, sql_helper, with_sqlalchemy_conn
from pyiem.nws.products.sigmet import parser
from pywwa.workflows.aviation import LOCS, load_database
from sqlalchemy.engine import Connection
from tqdm import tqdm

year = sys.argv[1]


@with_sqlalchemy_conn("postgis")
def get_archive(conn: Connection = None) -> pd.DataFrame:
    """Get our archive."""
    return gpd.read_postgis(
        sql_helper(f"""
        select ctid, product_id, issue, label, geom from sigmets_{year} where
        st_isvalid(geom) and product_id is not null and
        issue > '2021-08-11'
        order by issue asc
        """),
        conn,
    )  # type: ignore


def main():
    """Go Main Go."""
    pgconn, cursor = get_dbconnc("postgis")
    load_database(cursor)
    entries = get_archive()
    print(f"Found {len(entries.index)}")
    progress = tqdm(entries.iterrows(), total=len(entries.index))
    updates = 0
    for _idx, row in progress:
        progress.set_description(f"Updated {updates} {row['issue']}")
        try:
            resp = httpx.get(
                "https://mesonet.agron.iastate.edu"
                f"/api/1/nwstext/{row['product_id']}"
            )
            resp.raise_for_status()
            prod = parser(
                resp.text,
                ugc_provider={},
                nwsli_provider=LOCS,
                utcnow=row["issue"],
            )
            for sigmet in prod.sigmets:
                if sigmet.label != row["label"]:
                    continue
                if abs(sigmet.geom.area - row["geom"].area) < 0.1:
                    continue
                cursor.execute(
                    f"UPDATE sigmets_{year} SET geom = %s WHERE ctid = %s",
                    (sigmet.geom.wkt, row["ctid"]),
                )
                updates += 1
                if updates % 100 == 0:
                    cursor.close()
                    pgconn.commit()
                    cursor = pgconn.cursor()

        except Exception as exp:
            print(f"Failed to parse {row['ctid']} {exp}")
            continue
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
