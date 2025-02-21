"""See if we have metadata in a local CSV file."""

import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn

CSVFN = "/home/akrherz/Downloads/nwsli_database.csv"


def dowork(df, nwsli):
    """do work!"""
    df2 = df[df["NWSLI"] == nwsli]
    if df2.empty:
        return
    row = df2.iloc[0]
    with get_dbconn("mesosite") as dbconn:
        cursor = dbconn.cursor()
        print("------")
        nwsli = row["NWSLI"]
        city = (
            f"{row['City']} {row['Detail']}{row['Direction']} - "
            f"{row['Station Name']}"
        )
        state = row["State"]
        network = f"{state}_DCP"
        print(nwsli)
        print(city)
        print(row["State"])
        print(f"Program {row['Program']}")
        print(f"Lat: {row['Latitude']} Lon: {row['Longitude']}")
        res = input(f"Enter City [{city}]: ")
        city = city if res == "" else res
        res = input(f"Enter network [{network}]: ")
        network = network if res == "" else res
        res = input("Enter Country [US]: ")
        country = res if res != "" else "US"
        cursor.execute(
            "INSERT into stations (id, name, network, country, plot_name, "
            "state, elevation, online, metasite, geom) VALUES (%s, %s, %s, "
            "%s, %s, %s, %s, %s, %s, ST_Point(%s, %s, 4326))",
            (
                nwsli,
                city,
                network,
                country,
                city,
                state,
                -999,
                True,
                False,
                row["Longitude"],
                row["Latitude"],
            ),
        )
        cursor.close()
        dbconn.commit()


def main():
    """Go Main Go!"""
    with get_sqlalchemy_conn("hads") as conn:
        udf = pd.read_sql(
            "SELECT distinct nwsli, 1 as col from unknown ORDER by nwsli",
            conn,
            index_col="nwsli",
        )
    print(f"Found {len(udf.index)} unknown entries")
    df = pd.read_csv(CSVFN, low_memory=False)
    for nwsli, _row in udf.iterrows():
        dowork(df, nwsli)


if __name__ == "__main__":
    main()
