#!/mesonet/python/bin/python

import mx.DateTime, pg
from pyIEM import stationTable, iemdb
i = iemdb.iemdb()
mydb = i["snet"]
st = stationTable.stationTable("/mesonet/TABLES/snet.stns")

Odur = {}
Ocnt = {}
for station in st.ids:
  Odur[station] = 0
  Ocnt[station] = 0

s = mx.DateTime.DateTime(2002,1,1)
end = mx.DateTime.DateTime(2006,10,1)

now = s
inter = mx.DateTime.RelativeDateTime(months=+1)

while ( now < end ):
  tbl = now.strftime("%Y_%m")
  rs = mydb.query("select min(valid), count(valid), station \
    from t"+tbl+" GROUP by station").dictresult()

  for i in range(len(rs)):
    station = rs[i]["station"]
    if (Ocnt.has_key(station)):
      Ocnt[station] += int(rs[i]["count"])
      if (Odur[station] == 0):
        Odur[station] = rs[i]["min"]

  now = now + inter

for station in st.ids:
  if (Odur[station] > 0):
    ts = mx.DateTime.strptime( Odur[station][:16] , '%Y-%m-%d %H:%M')
    psec = float(Ocnt[station]) / (float(end - ts) / 60 )
    print "%s,%s,%s,%s" % (station, Odur[station], Ocnt[station], psec * 100)
