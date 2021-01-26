"""One time, the NWS could not issue LSRs, so I tried."""
import datetime
import requests
from pyiem.util import get_dbconn

data = """238 PM	West Des Moines	3
327 PM	Clive	4.5
840 PM	Fort Dodge	3"""

pgconn = get_dbconn("postgis")
cursor = pgconn.cursor()
for line in data.split("\n"):
    tokens = line.replace("~", "").split()
    dt = datetime.datetime.strptime(
        f"2021-01-25 {tokens[0]} {tokens[1]}", "%Y-%m-%d %I%M %p"
    )
    # print(dt)
    place = " ".join(tokens[2:-1])
    if place.find("(") > -1:
        place = place[: place.find("(")]
    url = (
        "http://mesonet.agron.iastate.edu/cgi-bin/geocoder.py?"
        f"address={place},IA"
    )
    content = requests.get(url).content.decode("ascii")
    if content.find(",") == -1:
        continue
    lat, lon = content.split(",")
    lat = float(lat)
    lon = float(lon)
    cursor.execute(
        "SELECT name from ugcs where substr(ugc, 1, 3) = 'IAC' and "
        "ST_Contains(geom, ST_SetSRID(ST_GeomFromEWKT('POINT(%s %s)'), 4326)) "
        "and end_ts is null and wfo = 'DMX'",
        (lon, lat),
    )
    row = cursor.fetchone()
    if row is None:
        continue
    name = row[0].upper()
    # print(name)
    # print(f"{place} {content}")

    stamp = dt.strftime("%02I%M %p")
    place = place.upper()
    lon = 0 - lon
    mag = "%.1f INCH" % (float(tokens[-1]),)
    print(
        f"{stamp}     SNOW             {place:23s} {lat:.2f}N {lon:.2f}W\n"
        f"01/25/2021  M{mag:10s}      {name:18s} IA   PUBLIC\n"
    )
