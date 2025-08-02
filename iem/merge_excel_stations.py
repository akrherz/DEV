"""we get an excel file with station locations, so we merge"""

import click
import pandas as pd
from pyiem.database import get_dbconn


@click.command()
@click.option("--filename", type=str, required=True)
def main(filename: str):
    """Go!"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    df = pd.read_csv(filename)
    for _, row in df.iterrows():
        nwsli = row["nwsli"]
        cursor.execute(
            (
                "UPDATE stations SET geom=ST_Point(%s, %s, 4326), "
                "county = null, elevation = null, ugc_zone = null, "
                "name = %s, plot_name = %s "
                " WHERE network in ('NE_COOP', 'KS_COOP') and id = %s"
            ),
            (
                row["lon"],
                row["lat"],
                row["name"],
                row["name"],
                nwsli,
            ),
        )
        if cursor.rowcount == 0:
            print(f"Failed to update {nwsli} {row['name']}")

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
