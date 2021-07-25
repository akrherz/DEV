"""See if we have metadata in a local CSV file

NOTE: I had to manually edit the .csv file to remove the first row
"""
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

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
        city = "%s %s%s - %s" % (
            row["City"],
            row["Detail"],
            row["Direction"],
            row["Station Name"],
        )
        state = row["State"]
        network = f"{state}_DCP"
        print(nwsli)
        print(city)
        print(row["State"])
        print(f"Program {row['Program']}")
        print("Lat: %s Lon: %s" % (row["Latitude"], row["Longitude"]))
        res = input(f"Enter City [{city}]: ")
        city = city if res == "" else res
        res = input(f"Enter network [{network}]: ")
        network = network if res == "" else res
        res = input("Enter Country [US]: ")
        country = res if res != "" else "US"
        cursor.execute(
            "INSERT into stations (id, name, network, country, plot_name, "
            "state, elevation, online, metasite, geom) VALUES (%s, %s, %s, "
            "%s, %s, %s, %s, %s, %s, 'SRID=4326;POINT(%s %s)')",
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
                float(row["Longitude"]),
                float(row["Latitude"]),
            ),
        )
        cursor.close()
        dbconn.commit()


def main():
    """Go Main Go!"""
    pgconn = get_dbconn("hads", user="mesonet")
    udf = read_sql(
        "SELECT distinct nwsli, 1 as col from unknown ORDER by nwsli",
        pgconn,
        index_col="nwsli",
    )
    print("Found %s unknown entries" % (len(udf.index),))
    df = pd.read_csv(CSVFN, low_memory=False)
    for nwsli, _row in udf.iterrows():
        dowork(df, nwsli)


if __name__ == "__main__":
    main()
