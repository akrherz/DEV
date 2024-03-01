"""Create scenario CLI files for later editing."""

import shutil

from pandas.io.sql import read_sql
from pyiem.dep import get_cli_fname
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    scenario = 140
    hucs = [x.strip() for x in open("myhucs.txt")]
    # Figure out the centroid of each
    df = read_sql(
        "SELECT huc_12, st_x(ST_transform(ST_centroid(geom), 4326)) as lon, "
        "st_y(ST_transform(ST_centroid(geom), 4326)) as lat from huc12 where "
        "scenario = 0 and huc_12 in %s",
        get_dbconn("idep"),
        params=(tuple(hucs),),
        index_col="huc_12",
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
