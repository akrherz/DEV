#!/mesonet/python/bin/python
#  Need to be more precise with outage data
#  Daryl Herzmann 8 Dec 2003

import re, mx.DateTime
from pyIEM import stationTable, iemdb
i = iemdb.iemdb()
st = stationTable.stationTable("/mesonet/TABLES/kcci.stns")
mydb = i['portfolio']

s = mx.DateTime.DateTime(2002,7,1)
e = mx.DateTime.DateTime(2006,3,1)


Odur = {}
Ocnt = {}
DBcnt = {}
outages = {}
for station in st.ids:
  Odur[station] = 0
  Ocnt[station] = 0
  outages[station] = []
  DBcnt[station] = 0

tickets = mydb.query("SELECT * from tt_base WHERE portfolio = 'kccisnet' \
  and subject = 'Site Offline' and author = 'mesonet' \
  and entered > '2002-07-01' \
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
    ts = mx.DateTime.strptime( backOnline[:16] , '%Y-%m-%d %H:%M')
    tsKey = ts.strftime("%Y%m%d%H")
    if not hrCnt.has_key(tsKey):
      hrCnt[tsKey] = 1
    else:
      hrCnt[tsKey] += 1

# Loop through the tickets again :(
for i in range(len(tickets)):
  id = str(tickets[i]["id"])
  s_mid = tickets[i]["s_mid"]
  if (s_mid[0] == "W"):
    continue
  entered = tickets[i]["entered"]
  ets = mx.DateTime.strptime( entered[:16], '%Y-%m-%d %H:%M')
  log = mydb.query("SELECT * from tt_log WHERE tt_id = "+ id +" \
    and comments ~* 'Site Back Online at:' ").dictresult()
  if len(log) == 1:
    comments = log[0]["comments"]
    tokens = re.split(" ", comments)
    backOnline = tokens[-2] +" "+ tokens[-1]
    ts = mx.DateTime.strptime( backOnline , '%Y-%m-%d %H:%M:%S.00')
    tsKey = ts.strftime("%Y%m%d%H")
    if (hrCnt[tsKey] < 30):  # We count it!!!
      Odur[s_mid] += ts - ets
      outages[s_mid].append( ts - ets )
      Ocnt[s_mid] += 1

for station in st.ids:
  if station[0] != "W":
    o = outages[station]
    day1 = 0
    day3 = 0
    day5 = 0
    day10 = 0
    for ot in o:
      if (ot > (86400 * 10)):
        day10 += 1
      elif (ot > (86400 * 5)):
        day5 += 1
      elif (ot > (86400 * 3)):
        day3 += 1
      elif (ot > (86400 * 1)):
        day1 += 1

    print "%s,%s,%s,%s,%s,%s,%s,%s,%s" % ( station, st.sts[station]['name'], \
      Ocnt[station],  day1, day3, day5, day10, \
      Odur[station].strftime("%d days and %H hours"), \
      100 * (1 - (Odur[station] / (e - s)))  ) 
