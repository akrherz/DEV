"""Cross check NWPS."""

import httpx
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper


def dowork(conn, df2, nwsli):
    """do work!"""
    row = df2.iloc[0]
    print("------")
    nwsli = row["NWSLI"]
    city = row["Station Name"]
    state = row["State"]
    network = f"{state}_DCP"
    print(nwsli)
    print(city)
    print(row["State"])
    print(f"Lat: {row['Latitude']} Lon: {row['Longitude']}")
    res = input(f"Enter City [{city}]: ")
    city = city if res == "" else res
    res = input(f"Enter network [{network}]: ")
    network = network if res == "" else res
    res = input("Enter Country [US]: ")
    country = res if res != "" else "US"
    conn.execute(
        sql_helper(
            "INSERT into stations (id, name, network, country, plot_name, "
            "state, elevation, online, metasite, geom) VALUES (:nwsli, :name, "
            ":network, :country, :name, :state, -999, 't', 'f', "
            "ST_Point(:lon, :lat, 4326))"
        ),
        {
            "nwsli": nwsli,
            "name": city,
            "network": network,
            "country": country,
            "state": state,
            "lat": row["Latitude"],
            "lon": row["Longitude"],
        },
    )


def main():
    """Go Main Go!"""
    with get_sqlalchemy_conn("hads") as conn:
        udf = pd.read_sql(
            sql_helper(
                "SELECT distinct nwsli, 1 as col from unknown ORDER by nwsli"
            ),
            conn,
            index_col="nwsli",
        )
    print(f"Found {len(udf.index)} unknown entries")
    meta: list[dict] = []
    resp = httpx.get("https://api.water.noaa.gov/nwps/v1/gauges", timeout=600)
    jdata = resp.json()
    for entry in jdata["gauges"]:
        meta.append(
            {
                "NWSLI": entry["lid"],
                "Station Name": entry["name"],
                "Latitude": entry["latitude"],
                "Longitude": entry["longitude"],
                "State": entry["state"]["abbreviation"],
            }
        )
    df = pd.DataFrame(meta)
    print(f"Found {len(df.index)} entries in NWPS")
    with get_sqlalchemy_conn("mesosite") as conn:
        for nwsli, _row in udf.iterrows():
            df2 = df[df["NWSLI"] == nwsli]
            if df2.empty:
                continue
            dowork(conn, df2, nwsli)
            conn.commit()


if __name__ == "__main__":
    main()
