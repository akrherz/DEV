"""figure out US landfalls in hurdat2"""
import datetime

import requests

import geopandas as gpd
import pandas as pd
from pyiem.util import get_sqlalchemy_conn
from shapely.geometry import Point


def main():
    """Go Main Go"""
    i = 0
    done = ["1997DANNYAL", "2017NATEMS"]  # HACK
    with get_sqlalchemy_conn("postgis") as conn:
        states = gpd.read_postgis(
            "SELECT state_abbr, the_geom from states",
            conn,
            geom_col="the_geom",
            index_col="state_abbr",
        )
    with open("hurdat2-1851-2021-041922.txt", encoding="ascii") as fh:
        for line in fh:
            tokens = line.split(",")
            if len(tokens) < 10:
                cane = tokens[1].strip()
                continue
            if cane == "LILI":  # no nexrad :/
                continue
            if tokens[2].strip() == "L" and tokens[3].strip() == "HU":
                # S Tip of Florida is 25N -81W
                lat = float(tokens[4][:-1])
                if lat < 25 or lat > 42:
                    continue
                lon = 0 - float(tokens[5][:-1])
                dt = datetime.datetime.strptime(
                    f"{tokens[0]}{tokens[1].strip()}",
                    "%Y%m%d%H%M",
                )
                if dt < datetime.datetime(1997, 1, 1):
                    continue
                dists = (
                    states.distance(Point(lon, lat))
                    .sort_values(ascending=True)
                    .head(1)
                )
                if dists.values[0] > 0.2:
                    print(dists)
                    continue
                state = dists.index[0]
                key = f"{dt.year}{cane}{state}"
                if key in done:
                    continue
                done.append(key)
                # 12 frames over 3 hours
                print(dt, cane, lat, lon, key)
                rng = datetime.timedelta(hours=6)
                for _dt in pd.date_range(dt - rng, dt + rng, freq="900S"):
                    uri = (
                        "https://mesonet.agron.iastate.edu/GIS/radmap.php?"
                        f"sector=conus&title={dt.year}%20{cane.title()}&ts="
                        f"{_dt:%Y%m%d%H%M}&layers[]=nexrad&layers[]=watches"
                    )
                    req = requests.get(uri, timeout=90)
                    with open(f"frames/{i:05.0f}.png", "wb") as fh:
                        fh.write(req.content)
                    i += 1
    print(len(done))


if __name__ == "__main__":
    main()
