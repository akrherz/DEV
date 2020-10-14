"""we get an excel file with station locations, so we merge"""

from pyiem.util import get_dbconn
from pyiem.network import Table as NetworkTable
from metpy.units import units as mpunits
import pandas as pd


def main():
    """Go!"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    ntcoop = NetworkTable("AZ_COOP")
    ntdcp = NetworkTable("AZ_DCP")
    df = pd.read_excel("/tmp/Station Contact Metadata.xlsx")
    # df2 = df[pd.notnull(df['NWS HB5 Name'])]
    # print(df2.columns)
    for _, row in df.iterrows():
        nwsli = row["SID"]
        if nwsli in ntdcp.sts:
            if nwsli in ntcoop.sts:
                print("%s is dual listed?" % (nwsli,))
            else:
                print("%s is DCP, move to COOP" % (nwsli,))
                cursor.execute(
                    (
                        "UPDATE stations SET network = 'AZ_COOP' WHERE "
                        "id = %s and network = 'AZ_DCP' "
                    ),
                    (nwsli,),
                )
        elev = (row["Elevation ft"] * mpunits("feet")).to(mpunits("meters"))
        cursor.execute(
            (
                "UPDATE stations SET geom='SRID=4326;POINT(%s %s)'"
                " , county = null, elevation = %s, ugc_zone = null, "
                "name = %s, plot_name = %s "
                " WHERE network in ('AZ_DCP', 'AZ_COOP') and id = %s"
            ),
            (
                row["Longitude"],
                row["Latitude"],
                elev.m,
                row["Site Name"],
                row["Site Name"],
                nwsli,
            ),
        )

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
