#!/mesonet/python/bin/python

from pyIEM import stationTable
st = stationTable.stationTable("/mesonet/TABLES/awos.stns")

lines = open("051206_awos.dat", 'r').readlines()

for line in lines:
  tokens = line.split(",")
  print "%s,%s,%s,%s,%s,%s,%s" % (tokens[0], st.sts[tokens[0]]['name'], st.sts[tokens[0]]['lat'], st.sts[tokens[0]]['lon'], tokens[1], tokens[2], tokens[-1]),
