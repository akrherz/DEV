"""See which stations need processing."""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import logger

LOG = logger()

PROBLEMS = [
    "CIR",  # archive has lots of just hourly precip
    "GVW",  # Missouri to Gulf traveller
]


def main():
    """Go Main."""
    countdf = pd.read_csv("ghcnh-inventory.txt", sep="\s+")
    countdf["annual"] = (
        countdf["JAN"]
        + countdf["FEB"]
        + countdf["MAR"]
        + countdf["APR"]
        + countdf["MAY"]
        + countdf["JUN"]
        + countdf["JUL"]
        + countdf["AUG"]
        + countdf["SEP"]
        + countdf["OCT"]
        + countdf["NOV"]
        + countdf["DEC"]
    )
    inventory = countdf.groupby("GHCNh_ID").agg(
        min_year=("YEAR", "min"),
        max_year=("YEAR", "max"),
        count=("YEAR", "count"),
        annual=("annual", "sum"),
    )

    with get_sqlalchemy_conn("mesosite") as conn:
        stationdf = pd.read_sql(
            sql_helper("""
    select id, value as ghcnh_id, archive_begin, network
    from station_attributes a JOIN stations t
    on (a.iemid = t.iemid) WHERE attr = 'GHCNH_ID' and network ~* 'ASOS'
            """),
            conn,
            index_col="id",
        )
    LOG.info("Found %s stations", len(stationdf))
    for sid in inventory[inventory["min_year"] == 2023].index:
        df2 = stationdf[stationdf["ghcnh_id"] == sid]
        if not df2.empty:
            print(sid, df2.iloc[0]["archive_begin"], df2.index[0])
    maxval = 0
    for sid, row in stationdf.iterrows():
        if sid in PROBLEMS:
            continue
        ghcnid = row["ghcnh_id"]
        if ghcnid not in inventory.index:
            LOG.info("Station %s GHCNH_ID %s not in inventory", sid, ghcnid)
            continue
        iemstart = row["archive_begin"].year
        nceistart = inventory.at[ghcnid, "min_year"]
        if nceistart < iemstart:
            obs = countdf[
                (countdf["GHCNh_ID"] == ghcnid) & (countdf["YEAR"] < iemstart)
            ]["annual"].sum()
            if obs > maxval:
                LOG.info(
                    "Station %s[%s] GHCNH_ID %s IEM:%s GHCN:%s OBS:%s",
                    sid,
                    row["network"],
                    ghcnid,
                    row["archive_begin"].year,
                    inventory.at[ghcnid, "min_year"],
                    obs,
                )
                maxval = obs


if __name__ == "__main__":
    main()
