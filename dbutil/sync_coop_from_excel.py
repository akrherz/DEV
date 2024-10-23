"""WFOs send me a spreadsheet of their sites, I should make magic happen."""

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from sqlalchemy import text


@click.command()
@click.option("--filename", required=True)
@click.option("--wfo", required=True)
def main(filename: str, wfo: str):
    """Go."""
    wfodf = pd.read_excel(filename, index_col="NWSLI")
    # Take the WFO's name and lat/lon verbatim
    with get_sqlalchemy_conn("mesosite") as pgconn:
        for nwsli, row in wfodf.iterrows():
            res = pgconn.execute(
                text(
                    "update stations SET name = :name, "
                    "geom = ST_Point(:lon, :lat, 4326), elevation = -999, "
                    "ugc_county = null, ugc_zone = null "
                    "WHERE id = :id and network ~* 'COOP'"
                ),
                {
                    "name": row["Name"],
                    "lon": row["Longitude"],
                    "lat": row["Latitude"],
                    "id": nwsli,
                },
            )
            if res.rowcount != 1:
                print(f"Failed to update {nwsli}")
            pgconn.commit()
    with get_sqlalchemy_conn("mesosite") as pgconn:
        iemdf = pd.read_sql(
            text(
                "select id, name from stations where network ~* 'COOP' and "
                "wfo = :wfo"
            ),
            pgconn,
            params={"wfo": wfo},
            index_col="id",
        )
    iem_delta = set(iemdf.index.values) - set(wfodf.index.values)
    wfo_delta = set(wfodf.index.values) - set(iemdf.index.values)
    print(f"iem delta: {iem_delta}")
    print(f"wfo delta: {wfo_delta}")
    # Work on IEM deltas
    with get_sqlalchemy_conn("mesosite") as pgconn:
        for nwsli in iem_delta:
            stdf = pd.read_sql(
                text(
                    "select wfo, network, online from stations where id = :id"
                ),
                pgconn,
                params={"id": nwsli},
            )
            print(f"----------- {nwsli}")
            print(stdf)
            print()


if __name__ == "__main__":
    main()
