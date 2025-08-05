"""Delete files without IEMRE support."""

import os
from datetime import date

import click
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.iemre import find_ij, get_grids
from tqdm import tqdm


@click.command()
@click.option("--domain", required=True)
def main(domain):
    """Go Main Go."""
    ds = get_grids(date(2007, 1, 2), domain=domain, varnames=["high_tmpk"])
    with get_sqlalchemy_conn(f"dep_{domain}") as conn:
        res = conn.execute(
            sql_helper("""
    select filepath, st_x(geom), st_y(geom), ctid from climate_files
    where scenario = 0 ORDER by st_y(geom) asc
                                  """),
        )
        good = 0
        bad = 0
        progress = tqdm(res.fetchall(), total=res.rowcount)
        for row in progress:
            progress.set_description(f"Good: {good} Bad: {bad}")
            i, j = find_ij(row[1], row[2], domain=domain)
            val = ds["high_tmpk"][j, i]
            if val >= 0:
                good += 1
                continue
            if os.path.isfile(row[0]):
                os.unlink(row[0])
            conn.execute(
                sql_helper("delete from climate_files where ctid = :c"),
                {"c": row[3]},
            )
            conn.commit()
            bad += 1
        print(good, bad)


if __name__ == "__main__":
    main()
