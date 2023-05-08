"""Example using the Cow API to generate a shapefile."""
import json
from io import BytesIO

import requests

import geopandas as gpd


def main():
    """Our main method."""
    url = (
        "https://mesonet.agron.iastate.edu/api/1/cow.json?wfo=DMX&"
        "begints=2019-01-01T00:00Z&endts=2019-08-06T00:00Z&"
        "phenomena=TO&lsrtype=TO&"
    )
    reg = requests.get(url, timeout=300)
    jsobj = reg.json()
    for name in ["events", "stormreports"]:
        # This feels hacky, but I did not find another means yet to do it
        buf = BytesIO()
        buf.write(json.dumps(jsobj[name]).encode("ASCII"))
        buf.seek(0)
        events = gpd.read_file(buf)
        events.to_file(name + ".shp")


if __name__ == "__main__":
    main()
