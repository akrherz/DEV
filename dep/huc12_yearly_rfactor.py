"""Download DEP's climate file, compute r-factor, summarize by year, profit."""

import httpx
import pandas as pd
from dailyerosion.io.wepp import read_cli
from pyiem.database import get_sqlalchemy_conn, sql_helper


def main():
    """Go Main Go."""
    hucs = (
        "102400130204 102801020803 102300010606 071000040101 102400010102 "
        "070600010601 070802051004 102300020402 070600051102 071000080302 "
        "070801041201"
    )
    with get_sqlalchemy_conn("idep") as conn:
        pts = pd.read_sql(
            sql_helper("""
        with data as (
            select huc12, st_centroid(st_transform(geom, 4326)) as geo from
            wbd_huc12 where huc12 = ANY(:hucs))
        select huc12, st_x(geo) as lon, st_y(geo) as lat from data
                       """),
            conn,
            params={"hucs": hucs.split()},
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
        data["huc12"] = row.huc12
        dfs.append(data.reset_index())
    pd.concat(dfs).to_csv(
        "/tmp/huc12_yearly_rfactor.csv",
        index=False,
        float_format="%.2f",
    )


if __name__ == "__main__":
    main()
