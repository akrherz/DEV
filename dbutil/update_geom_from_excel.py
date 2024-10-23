"""Read Excel info an update geometry of IEMDB."""

import click
import pandas as pd
from pyiem.util import get_dbconnc


@click.command()
@click.option("--filename")
def main(filename):
    """Go."""
    pgconn, cursor = get_dbconnc("mesosite")
    df = pd.read_excel(filename, index_col="NWSLI")
    for nwsli, row in df.iterrows():
        sn = row["Station Name"]
        print(nwsli, row["Longitude"], row["Latitude"], sn)
        cursor.execute(
            "UPDATE stations SET geom = ST_POINT(%s, %s, 4326), name = %s, "
            "plot_name = %s WHERE id = %s and network ~* 'COOP'",
            (row["Longitude"], row["Latitude"], sn, sn, nwsli),
        )
        if cursor.rowcount == 0:
            print(f"ERROR: {nwsli} did not update")
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
