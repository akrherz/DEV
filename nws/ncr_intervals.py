import datetime

print("  Approx NWS Data Outages for 13 Jul 2016 (UTC)")
lts = datetime.datetime(2017, 7, 13)
for line in open('aa'):
  if line.find("Processed") == -1:
    continue
  ts = datetime.datetime.strptime("2016 " + line[:15], '%Y %b %d %H:%M:%S')
  if (ts - lts).total_seconds() > 120:
    print "    %s -> %s (%4i seconds) " % ((lts + datetime.timedelta(hours=5)).strftime("%H:%M:%S"),
        (ts + datetime.timedelta(hours=5)).strftime("%H:%M:%S"), (ts - lts).total_seconds())
  lts = ts
