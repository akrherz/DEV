#!/mesonet/python/bin/python

import pg, stationTable
st = stationTable.stationTable("/mesonet/TABLES/kcci.stns")
mydb = pg.connect("portfolio", "meteor.geol.iastate.edu")

#rs = mydb.query("SELECT name, email, s_mid from iem_site_contacts WHERE \
#  portfolio = 'kccisnet' and s_mid in ('SPKI4', 'SOCI4', 'SCEI4', 'SJCI4', 'SOGI4')").dictresult()
rs = mydb.query("SELECT name, email, s_mid from iem_site_contacts WHERE \
  portfolio = 'kelosnet'").dictresult()

for i in range(len(rs)):
  #print "%s,%s,%s,%s" % (rs[i]['s_mid'], st.sts[rs[i]['s_mid']]["name"], \
  print "%s" % (rs[i]["email"])