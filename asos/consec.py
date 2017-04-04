import psycopg2
import sys

site = sys.argv[1]
pgconn = psycopg2.connect(database='asos', host='localhost', port=5555,
                          user='nobody')
cursor = pgconn.cursor()

cursor.execute("""
  select valid, skyc1, skyc2, skyc3, skyc4 from alldata where station = %s and
  extract(hour from (valid + '10 minutes'::interval) at time zone 'UTC') = 15
  and report_type = 2 ORDER by valid
  """, (site,))
lastts = None
startts = None
maxperiod = [0, None, None]
for row in cursor:
    if lastts is None:
        lastts = row[0]
    overcast = ('OVC' in row[1:])
    if overcast:
        if startts is None:
            startts = row[0]
        period = (row[0] - startts).total_seconds()
        if period >= (86400. * 9.):
            print("%s -> %s %.0f days" % (startts.strftime("%-d %b %Y"),
                                          row[0].strftime("%-d %b %Y"),
                                          (period / 86400.) + 1.))
    else:
        if startts is not None:
            period = (row[0] - startts).total_seconds()
            if period > maxperiod[0]:
                maxperiod = [period, startts, row[0]]
                print("%s -> %s %.0f days" % (startts, row[0],
                                              period / 86400.))
        startts = None
