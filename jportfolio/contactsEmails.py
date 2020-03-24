#!/mesonet/python/bin/python

import pg
mydb = pg.connect('portfolio', 'meteor.geol.iastate.edu', 5432)

rs = mydb.query("SELECT distinct email from iem_site_contacts WHERE \
  portfolio = 'kccisnet'").dictresult()

for i in range(len(rs)):
  print rs[i]["email"] , "," ,
