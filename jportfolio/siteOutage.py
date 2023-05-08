# Extract Stats about site outages...
# Daryl Herzmann 15 Jul 2002
#  8 Jan 2003	Only include Sites offline messages

import pg
import stationTable

st = stationTable.stationTable("/mesonet/TABLES/awos.stns")
mydb = pg.connect("portfolio", "meteor.geol.iastate.edu", 5432)

outs = {}
for stn in st.ids:
    outs[stn] = {"count": 0, "length": 0}


def Main():
    rs = mydb.query(
        "select s_mid, count(entered), sum(age(last, entered)) \
   from tt_base WHERE portfolio = 'iaawos' and \
   subject = 'Site Offline' and \
   status = 'CLOSED' GROUP by s_mid"
    ).dictresult()
    for i in range(len(rs)):
        outs[rs[i]["s_mid"]]["count"] = rs[i]["count"]
        outs[rs[i]["s_mid"]]["length"] = rs[i]["sum"]

    for stn in outs.keys():
        print(
            "%s,%s,%s,%s"
            % (
                stn,
                st.sts[stn]["name"],
                outs[stn]["count"],
                outs[stn]["length"],
            )
        )


Main()
