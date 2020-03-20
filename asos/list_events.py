"""List out some presentwx events."""
import datetime
import sys
from pyiem.util import get_dbconn

site = sys.argv[1]
pgconn = get_dbconn("asos")
cursor = pgconn.cursor()

cursor.execute(
    """
  select valid, presentwx from alldata where station = %s
  and (presentwx ~* 'IP' or presentwx ~* 'PL') ORDER by valid
  """,
    (site,),
)
lastts = None
startts = None
for row in cursor:
    if lastts is None:
        lastts = row[0]
    if (row[0] - lastts) > datetime.timedelta(hours=1):
        if startts is not None and (lastts - startts) >= datetime.timedelta(
            hours=1
        ):
            print(
                "%s,%s,%s,%s"
                % (
                    site,
                    startts,
                    lastts,
                    (lastts - startts).total_seconds() / 60.0,
                )
            )
        startts = row[0]
    lastts = row[0]
