import psycopg2
import datetime
import sys

site = sys.argv[1]
pgconn = psycopg2.connect(database='asos', host='localhost', port=5555,
                          user='nobody')
cursor = pgconn.cursor()

cursor.execute("""
  select valid, presentwx from alldata where station = %s
  and (presentwx ~* 'IP' or presentwx ~* 'PL') ORDER by valid
  """, (site,))
lastts = None
startts = None
for row in cursor:
    if lastts is None:
        lastts = row[0]
    if (row[0] - lastts) > datetime.timedelta(hours=1):
        if (startts is not None and
                (lastts - startts) >= datetime.timedelta(hours=1)):
            print("%s,%s,%s,%s" % (site, startts, lastts,
                                   (lastts - startts).total_seconds() / 60.))
        startts = row[0]
    lastts = row[0]
