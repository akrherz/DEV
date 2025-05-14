"""Fix the SIGMET archive..."""

import pandas as pd
from pyiem.database import get_dbconnc, sql_helper, with_sqlalchemy_conn
from pyiem.nws.products.sigmet import parser
from pyiem.util import noaaport_text
from pywwa.workflows.aviation import LOCS, load_database
from sqlalchemy.engine import Connection
from tqdm import tqdm


@with_sqlalchemy_conn("afos")
def get_archive(conn: Connection = None) -> pd.DataFrame:
    """Get our archive."""
    return pd.read_sql(
        sql_helper("""
        select entered, data from products where substr(pil, 1, 3) = 'SIG'
        and entered > '2005-01-01' and entered < '2006-01-01'
        order by entered asc
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
        progress.set_description(f"Updated {updates} {row['entered']}")
        try:
            prod = parser(
                noaaport_text(row["data"]),
                ugc_provider={},
                nwsli_provider=LOCS,
                utcnow=row["entered"],
            )
        except Exception as exp:
            progress.write(f"Failed to parse {row['entered']} {exp}")
            continue
        prod.sql(cursor)
        updates += 1
        if updates % 100 == 0:
            cursor.close()
            pgconn.commit()
            cursor = pgconn.cursor()
        """
        for sigmet in prod.sigmets:
            cursor.execute(
                "select ctid from sigmets_archive where label = %s and "
                "product_id is null and issue = %s and expire = %s and "
                "sigmet_type = 'C'",
                (sigmet.label, prod.valid, sigmet.ets)
            )
            if cursor.rowcount == 0:
                continue
            ctid = cursor.fetchone()['ctid']
            cursor.execute(
                "update sigmets_archive set product_id = %s where "
                "ctid = %s",
                (prod.get_product_id(), ctid)
            )
            updates += 1
            if updates % 100 == 0:
                cursor.close()
                pgconn.commit()
                cursor = pgconn.cursor()
        """
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
