"""NCEP NBM v5 upgrade bug has duplicate data for 38 stations.

11 May 2026 -> Reported to NCEP, they are working to fix, until then...
"""

from datetime import datetime, timezone

import click
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import logger

LOG = logger()


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
def main(valid: datetime):
    """Go Main."""
    valid = valid.replace(tzinfo=timezone.utc)
    with get_sqlalchemy_conn("mos") as conn:
        res = conn.execute(
            sql_helper(
                """
    with candidates as (
        select station, ftime, count(*), max(ctid) from t2026
        where runtime = :valid and  model = 'NBS' GROUP by station, ftime)
    delete from t2026 t using candidates c where t.model = 'NBS' and
    t.runtime = :valid and t.ctid = c.max and c.count = 2
    """
            ),
            {"valid": valid},
        )
        lvl = LOG.warning if res.rowcount == 0 else LOG.info
        lvl("Removed %s NBS rows for %s", res.rowcount, valid)
        conn.commit()


if __name__ == "__main__":
    main()
