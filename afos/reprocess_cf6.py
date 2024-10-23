"""Process TAFs again."""

import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.nws.products.cf6 import parser
from pyiem.util import logger
from tqdm import tqdm

LOG = logger()


def main():
    """Go Main Go."""
    dbconn, cursor = get_dbconnc("afos")
    adbconn, _acursor = get_dbconnc("iem")
    progress = tqdm(
        pd.date_range("2020/01/01", "2020/05/10", tz="UTC"), disable=False
    )
    for dt in progress:
        progress.set_description(f"{dt:%Y-%m-%d}")
        cursor.execute(
            """
            select entered, data from products where substr(pil, 1, 3) = 'CF6'
            and entered >= %s and entered < %s ORDER by entered ASC
    """,
            (dt, dt + pd.Timedelta(days=1)),
        )
        acursor = adbconn.cursor()
        for row in cursor:
            try:
                prod = parser(row["data"], utcnow=row["entered"])
                progress.set_description(prod.get_product_id())
            except Exception as exp:
                LOG.info("failed to parse %s: %s", row["data"], exp)
                continue
            prod.sql(acursor)
        acursor.close()
        adbconn.commit()


if __name__ == "__main__":
    main()
