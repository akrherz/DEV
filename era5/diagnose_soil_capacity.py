"""See what the database says about the soil capacity."""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn


def main():
    """."""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            """
            select id, value as soiltype
            from stations s JOIN station_attributes a
            on (s.iemid = a.iemid) WHERE attr = 'ERA5LAND_SOILTYPE' and
            network ~* 'CLIMATE' and archive_begin < '1950-01-01' and
            archive_end is null
            """,
            conn,
            index_col="id",
        )
    with get_sqlalchemy_conn("coop") as conn:
        obs = pd.read_sql(
            """
            select station, min(era5land_soilm1m_avg) as minval,
            max(era5land_soilm1m_avg) as maxval from alldata
            WHERE era5land_soilm1m_avg is not null
            GROUP by station
            """,
            conn,
            index_col="station",
        )

    df["minval"] = obs["minval"]
    df["maxval"] = obs["maxval"]
    for stype, gdf in df.groupby("soiltype"):
        print("\n\n-------------")
        print(stype)
        print(gdf["minval"].describe())
        print(gdf["maxval"].describe())


if __name__ == "__main__":
    main()
