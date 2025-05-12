"""Process TAFs again."""

import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.nws.products.taf import parser
from pyiem.util import logger
from tqdm import tqdm

LOG = logger()


def main():
    """Go Main Go."""
    dbconn, cursor = get_dbconnc("afos")
    adbconn, _acursor = get_dbconnc("asos")
    progress = tqdm(
        pd.date_range("2010/01/14", "2010/12/31", tz="UTC"), disable=False
    )
    for dt in progress:
        progress.set_description(f"{dt:%Y-%m-%d}")
        cursor.execute(
            """
            select entered, data from products where substr(pil, 1, 3) = 'TAF'
            and entered >= %s and entered < %s ORDER by entered ASC
    """,
            (dt, dt + pd.Timedelta(days=1)),
        )
        acursor = adbconn.cursor()
        for row in cursor:
            try:
                prod = parser(
                    row["data"], utcnow=row["entered"], ugc_provider={}
                )
            except Exception as exp:
                LOG.info("failed to parse %s: %s", row["data"], exp)
                continue
            prod.sql(acursor)
        acursor.close()
        adbconn.commit()


if __name__ == "__main__":
    main()
