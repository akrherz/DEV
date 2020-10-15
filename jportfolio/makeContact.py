# Add site contacts to the database
# Daryl Herzmann 5 Jul 2002
# 15 Apr 2005	Only add if they don't exist.

import pg
from pyIEM import stationTable

mydb = pg.connect("portfolio", "meteor.geol.iastate.edu", 5432)
st = stationTable.stationTable("/mesonet/TABLES/awos.stns")

portfolio = "iaawos"
name = "Allen Sells"
email = "allen.sells@dot.iowa.gov"

for station in st.ids:
    sql = (
        "SELECT * from iem_site_contacts WHERE portfolio = '%s' and \
         email = '%s' and s_mid = '%s'"
        % (portfolio, email, station)
    )
    rs = mydb.query(sql).dictresult()

    if len(rs) == 0:
        sql = (
            "INSERT into iem_site_contacts (portfolio, s_mid, \
           name, phone, email) VALUES ('%s', '%s', \
           '%s', ' ', '%s')"
            % (portfolio, station, name, email)
        )
        print("Adding for %s" % (station,))
        mydb.query(sql)
