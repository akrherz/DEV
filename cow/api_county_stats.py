"""Generate stats."""
import json
from io import BytesIO

import requests

import geopandas as gpd


def main():
    """Our main method."""
    url = (
        "https://mesonet.agron.iastate.edu/api/1/cow.json?wfo=EAX&"
        "begints=2008-01-01T00:00Z&endts=2022-12-31T00:00Z&"
        "phenomena=TO&lsrtype=TO&"
    )
    reg = requests.get(url, timeout=300)
    jsobj = reg.json()
    # This feels hacky, but I did not find another means yet to do it
    buf = BytesIO()
    buf.write(json.dumps(jsobj["events"]).encode("ASCII"))
    buf.seek(0)
    events = gpd.read_file(buf)
    idxs = []
    for idx, row in events.iterrows():
        if "MOC101" in row["ar_ugc"]:
            idxs.append(idx)
    df = events.loc[idxs]
    print(len(df.index), df["verify"].sum())
    buf = BytesIO()
    buf.write(json.dumps(jsobj["stormreports"]).encode("ASCII"))
    buf.seek(0)
    reports = gpd.read_file(buf)
    df = reports[(reports["county"] == "JOHNSON") & (reports["state"] == "MO")]
    print(len(df.index))


if __name__ == "__main__":
    main()
