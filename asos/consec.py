"""General consec analysis."""
from __future__ import print_function
import sys

from pyiem.util import get_dbconn

site = sys.argv[1]
pgconn = get_dbconn("asos")
cursor = pgconn.cursor()

cursor.execute(
    """
  select valid, round(tmpf::numeric, 0) from alldata where station = %s and
  extract(minute from valid) in (53, 0) and tmpf is not null
  and report_type = 2 ORDER by valid ASC
  """,
    (site,),
)
lastval = 0
running = []
for row in cursor:
    if (lastval - row[1]) == 1:
        running.append(row[0])
        lastval = row[1]
        continue
    if len(running) > 10:
        print("%s %s" % (len(running), running))
    lastval = row[1]
    running = []
