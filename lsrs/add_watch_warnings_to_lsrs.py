"""Requested one-off."""

from datetime import timezone

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import logger
from sqlalchemy import text
from tqdm import tqdm

LOG = logger()


@click.command()
@click.option("--year", type=int)
@click.option("--state", default="AL")
def main(year, state):
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        lsrs = pd.read_sql(
            text(f"""
            select valid at time zone 'UTC' as utc_valid,
            st_x(l.geom) as lon, st_y(l.geom) as lat,
            'https://mesonet.agron.iastate.edu/p.php?pid=' || product_id
                as lsr_link,
            typetext, city, county, l.wfo, ugc from lsrs_{year} l
            JOIN ugcs u on (l.gid = u.gid) where
            l.state = :state
            and l.type in ('D', 'H', 'G', 'T') order by valid asc
            """),
            conn,
            params={"year": year, "state": state},
        )
        lsrs["utc_valid"] = lsrs["utc_valid"].dt.tz_localize(timezone.utc)
        lsrs["tornado_watch"] = ""
        lsrs["severe_tstorm_watch"] = ""
        lsrs["tornado_warning"] = ""
        lsrs["severe_tstorm_warning"] = ""
        LOG.info("Process Watches")
        for idx, row in tqdm(lsrs.iterrows(), total=len(lsrs.index)):
            res = conn.execute(
                text("""
                select phenomena, eventid, significance
                from warnings where vtec_year = :year and
                ugc = :ugc and issue <= :utc_valid and expire > :utc_valid
                and phenomena in ('TO', 'SV') and significance = 'A'
                """),
                {
                    "ugc": row["ugc"],
                    "utc_valid": row["utc_valid"],
                    "year": year,
                },
            )
            if res.rowcount == 0:
                continue
            for row2 in res:
                cc = "tornado" if row2[0] == "TO" else "severe_tstorm"
                lsrs.at[idx, f"{cc}_watch"] = row2[1]

        LOG.info("Process Warnings")
        for idx, row in tqdm(lsrs.iterrows(), total=len(lsrs.index)):
            res = conn.execute(
                text("""
                select wfo, phenomena, eventid, significance
                from sbw where vtec_year = :year and status = 'NEW' and
                issue <= :utc_valid and expire > :utc_valid
                and phenomena in ('TO', 'SV') and significance = 'W'
                and ST_Contains(geom, ST_Point(:lon, :lat, 4326))
                """),
                {
                    "lon": row["lon"],
                    "lat": row["lat"],
                    "utc_valid": row["utc_valid"],
                    "year": year,
                },
            )
            if res.rowcount == 0:
                continue
            for row2 in res:
                cc = "tornado" if row2[1] == "TO" else "severe_tstorm"
                url = (
                    "https://mesonet.agron.iastate.edu/vtec/"
                    f"#2024-O-NEW-K{row2[0]}-{row2[1]}-W-{row2[2]:04d}"
                )
                label = f"{row2[0]}.{row2[1]}.{row2[2]}"
                lsrs.at[idx, f"{cc}_warning"] = f"{label} {url}"

    lsrs["utc_valid"] = lsrs["utc_valid"].dt.strftime("%Y-%m-%dT%H:%M")
    with pd.ExcelWriter(f"lsrs_{year}.xlsx") as writer:
        lsrs.to_excel(writer, sheet_name="lsrs", index=False)
        worksheet = writer.sheets["lsrs"]
        for idx, row in lsrs.iterrows():
            cell = f"L{idx + 2}"
            if row["tornado_warning"] != "":
                link, url = row["tornado_warning"].split()
                worksheet.write_url(cell, url, string=link)
            cell = f"M{idx + 2}"
            if row["severe_tstorm_warning"] != "":
                link, url = row["severe_tstorm_warning"].split()
                worksheet.write_url(cell, url, string=link)


if __name__ == "__main__":
    main()
