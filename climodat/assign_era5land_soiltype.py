"""Set a database attribute for the soil type of the ERA5-Land grid cells.

Get slt.nc from
https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation
"""

import numpy as np

import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.util import ncopen

ATTRNAME = "ERA5LAND_SOILTYPE"
SOILTYPES = {
    0: "Missing",
    1: "Coarse",
    2: "Medium",
    3: "Medium fine",
    4: "Fine",
    5: "Very fine",
    6: "Organic",
    7: "Tropical organic",
}


def main():
    """."""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            "SELECT iemid, st_x(geom) as lon, st_y(geom) as lat from stations "
            "WHERE network ~* 'CLIMATE'",
            conn,
            index_col="iemid",
        )
    with ncopen("slt.nc") as nc:
        lons = nc.variables["longitude"][:]
        lats = nc.variables["latitude"][:]
        slt = nc.variables["slt"][:].astype(int)

    df["lon"] = df["lon"].apply(lambda x: x if x > 0 else x + 360)
    df["gridx"] = np.digitize(df["lon"].values, lons)
    df["gridy"] = np.digitize(df["lat"].values, lats)
    pgconn, cursor = get_dbconnc("mesosite")
    for iemid, row in df.iterrows():
        soiltype = SOILTYPES[slt[0, int(row["gridy"]), int(row["gridx"])]]
        cursor.execute(
            "delete from station_attributes where iemid = %s and attr = %s",
            (iemid, ATTRNAME),
        )
        cursor.execute(
            "INSERT into station_attributes(iemid, attr, value) "
            "VALUES (%s, %s, %s)",
            (iemid, ATTRNAME, soiltype),
        )
    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
