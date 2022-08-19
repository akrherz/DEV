"""See what Dr Thompson has to say."""

import requests
from pyiem.util import get_dbconn


def main():
    """Go."""
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()
    asos = get_dbconn("asos")
    acursor = asos.cursor()
    acursor.execute("select distinct id from unknown")
    unknown = []
    for row in acursor:
        unknown.append(row[0])
    req = requests.get("https://weather.rap.ucar.edu/surface/stations.txt")
    for line in req.text.split("\n"):
        if line.startswith("!") or len(line) < 80:
            continue
        sid4 = line[20:24]
        if sid4 not in unknown:
            continue
        if not sid4.startswith("C"):
            print(line)
            continue
        lat = int(line[39:41])
        lat += float(line[42:44]) / 60.0
        lon = 0 - int(line[47:50])
        lon -= float(line[51:53]) / 60.0
        network = f"CA_{line[:2]}_ASOS"
        print(network, sid4, lon, lat)
        mcursor.execute(
            "INSERT into stations (id, name, network, country, plot_name, "
            "state, elevation, online, metasite, geom) VALUES (%s, %s, %s, "
            "%s, %s, %s, %s, %s, %s, 'SRID=4326;POINT(%s %s)')",
            (
                sid4,
                line[3:19].strip(),
                network,
                "CA",
                line[3:19].strip(),
                line[:2],
                -999,
                False,
                False,
                lon,
                lat,
            ),
        )
    mcursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
