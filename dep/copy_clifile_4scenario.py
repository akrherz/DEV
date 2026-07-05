"""Create scenario CLI files for later editing."""

import shutil

from pandas.io.sql import read_sql
from pyiem.database import get_dbconn
from pyiem.dep import get_cli_fname


def main():
    """Go Main Go."""
    scenario = 140
    hucs = [x.strip() for x in open("myhucs.txt")]
    # Figure out the centroid of each
    df = read_sql(
        """
        SELECT huc12_code, st_x(ST_transform(ST_centroid(geom), 4326)) as lon,
        st_y(ST_transform(ST_centroid(geom), 4326)) as lat from huc12 where
        scenario_id = 0 and huc12_code in %s""",
        get_dbconn("dep"),
        params=(tuple(hucs),),
        index_col="huc12_code",
    )
    for huc_12, row in df.iterrows():
        clifn = get_cli_fname(row["lon"], row["lat"])
        shutil.copyfile(clifn, f"/i/{scenario}/cli/{huc_12}.cli")
        print(
            f"python extract_timeseries.py {row['lon']} {row['lat']} "
            f"{huc_12}.csv"
        )


if __name__ == "__main__":
    main()
