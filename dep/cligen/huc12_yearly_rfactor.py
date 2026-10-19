"""Download DEP's climate file, compute r-factor, summarize by year, profit."""

from datetime import date

import httpx
import pandas as pd
from dailyerosion.io.wepp import read_cli
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    up_till_year = date.today().year
    hucs = ("102400130204 071000050204").split()
    with get_sqlalchemy_conn("dep") as conn:
        pts = pd.read_sql(
            sql_helper("""
        with data as (
            select huc12_code, st_centroid(st_transform(geom, 4326)) as geo
            from huc12 where huc12_code = ANY(:hucs) and scenario_id = 0)
        select huc12_code, st_x(geo) as lon, st_y(geo) as lat from data
                       """),
            conn,
            params={"hucs": hucs},
        )
    if len(pts.index) != len(hucs):
        LOG.warning(
            "Mismatch len(hucs)=%s len(pts)=%s", len(hucs), len(pts.index)
        )
    dfs = []
    for row in pts.itertuples():
        resp = httpx.get(
            "https://mesonet-dep.agron.iastate.edu/dl/climatefile.py?"
            f"lat={row.lat}&lon={row.lon}",
            timeout=30,
        )
        with open("/tmp/dep.cli", "w") as fh:
            fh.write(resp.text)
        cli = read_cli("/tmp/dep.cli", compute_rfactor=True)
        data = cli.groupby(cli.index.year).sum(numeric_only=True).copy()
        data.index.name = "year"
        data["huc12"] = row.huc12_code
        dfs.append(data.loc[:up_till_year].reset_index())
    pd.concat(dfs).to_csv(
        "/tmp/huc12_yearly_rfactor.csv",
        index=False,
        float_format="%.2f",
    )


if __name__ == "__main__":
    main()
