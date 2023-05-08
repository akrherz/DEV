#  Need to be more precise with outage data
#  Daryl Herzmann 8 Dec 2003

import mx.DateTime
import pg

mydb = pg.connect("portfolio", "meteor.geol.iastate.edu", 5432)

s = mx.DateTime.DateTime(2002, 6, 25)
e = mx.DateTime.DateTime(2005, 12, 1)


sql = "SELECT count(distinct s_mid) as stations, count(*) as count, \
  extract(year from entered) as year,\
  extract(month from entered) as month from tt_base WHERE \
  subject = 'Site Offline' and author = 'mesonet' \
  GROUP by year, month"
print(sql)
tickets = mydb.query(sql).dictresult()

for i in range(len(tickets)):
    print(
        "%s,%s,%s,%s"
        % (
            tickets[i]["year"],
            tickets[i]["month"],
            tickets[i]["count"],
            tickets[i]["stations"],
        )
    )
