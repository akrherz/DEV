import pg
import stationTable

st = stationTable.stationTable("/mesonet/TABLES/kcci.stns")
mydb = pg.connect("portfolio", "meteor.geol.iastate.edu")

rs = mydb.query(
    "SELECT name, email, s_mid from iem_site_contacts WHERE \
  portfolio = 'kelosnet'"
).dictresult()

for i in range(len(rs)):
    print("%s" % (rs[i]["email"]))
