#!/mesonet/python/bin/python
#  Need to be more precise with outage data
#  Daryl Herzmann 8 Dec 2003

import pg, re, mx.DateTime, stationTable
st = stationTable.stationTable("/mesonet/TABLES/awos.stns")
mydb = pg.connect("portfolio", "meteor.geol.iastate.edu", 5432)

s = mx.DateTime.DateTime(2003,1,1)
e = mx.DateTime.DateTime(2005,12,6)


Odur = {}
Ocnt = {}
DBcnt = {}
for station in st.ids:
  Odur[station] = 0
  Ocnt[station] = 0
  DBcnt[station] = 0

tickets = mydb.query("SELECT * from tt_base WHERE portfolio = 'iaawos' \
  and subject = 'Site Offline' and author = 'mesonet' \
  and entered > '2003-01-01' \
  ORDER by id ASC").dictresult()

hrCnt = {}

for i in range(len(tickets)):
  id = str(tickets[i]["id"])
  log = mydb.query("SELECT * from tt_log WHERE tt_id = "+ id +" \
    and comments ~* 'Site Back Online at:' ").dictresult()
  if len(log) == 1:
    comments = log[0]["comments"]
    tokens = re.split(" ", comments)
    backOnline = tokens[-2] +" "+ tokens[-1]
    ts = mx.DateTime.strptime( backOnline , '%Y-%m-%d %H:%M:00.00')
    tsKey = ts.strftime("%Y%m%d%H")
    if not hrCnt.has_key(tsKey):
      hrCnt[tsKey] = 1
    else:
      hrCnt[tsKey] += 1

# Loop through the tickets again :(
for i in range(len(tickets)):
  id = str(tickets[i]["id"])
  s_mid = tickets[i]["s_mid"]
  entered = tickets[i]["entered"]
  ets = mx.DateTime.strptime( entered[:16], '%Y-%m-%d %H:%M')
  log = mydb.query("SELECT * from tt_log WHERE tt_id = "+ id +" \
    and comments ~* 'Site Back Online at:' ").dictresult()
  if len(log) == 1:
    comments = log[0]["comments"]
    tokens = re.split(" ", comments)
    backOnline = tokens[-2] +" "+ tokens[-1]
    ts = mx.DateTime.strptime( backOnline , '%Y-%m-%d %H:%M:00.00')
    tsKey = ts.strftime("%Y%m%d%H")
    if (hrCnt[tsKey] < 30):  # We count it!!!
      Odur[s_mid] += ts - ets
      Ocnt[s_mid] += 1

for station in st.ids:
  if station != "CWI" and station != "FOD":
    print "%s,%s,%s,%s,%s" % ( station, st.sts[station]['name'], \
      Ocnt[station],  Odur[station].strftime("%d days and %H hours"), \
      100 * (1 - (Odur[station] / (e - s)))  ) 
