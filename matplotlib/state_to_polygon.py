import re
import sys

import iemdb

POSTGIS = iemdb.connect("postgis", bypass=True)
pcursor = POSTGIS.cursor()

pcursor.execute(
    """
 select ST_asText(ST_convexhull(ST_collect( the_geom ))) from states 
 where state_abbr in ('IA','MO', 'KY','OH','IN','IL','MI','WI','MN','ND','SD','KS', 'NE')
"""
)

row = pcursor.fetchone()

o = open(sys.argv[1], "w")

wkt = row[0]
lines = re.findall("\(([\.\,\-0-9\s]+)\)", wkt)
for line in lines:
    x = []
    y = []
    tokens = line.split(",")
    for token in tokens:
        lon, lat = token.split()
        x.append(lon)
        y.append(lat)

    o.write(
        str(x)
        .replace(",", "")
        .replace("'", "")
        .replace("[", "")
        .replace("]", "")
        + "\n"
    )
    o.write(
        str(y)
        .replace(",", "")
        .replace("'", "")
        .replace("[", "")
        .replace("]", "")
        + "\n"
    )
o.close()
