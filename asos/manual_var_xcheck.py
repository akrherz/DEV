"""Try to do some QC, one time, please."""

from zoneinfo import ZoneInfo

import click
import pandas as pd
from pyiem.database import (
    get_dbconnc,
    get_sqlalchemy_conn,
    sql_helper,
    with_sqlalchemy_conn,
)
from pyiem.network import Table as NetworkTable
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()


def process(
    conn,
    row,
    station,
    nt,
    varname: str,
    neighbors: pd.DataFrame,
    autozap: bool,
):
    """Do what we need to do here."""
    delta = pd.Timedelta(hours=1)
    obs = pd.read_sql(
        sql_helper(
            """
    SELECT station, valid, {varname} from alldata where
    station = ANY(:stations) and valid >= :sts and valid <= :ets and
    {varname} is not null ORDER by {varname} ASC
        """,
            varname=varname,
        ),
        conn,
        params={
            "stations": neighbors.index.tolist(),
            "sts": row["valid"] - delta,
            "ets": row["valid"] + delta,
        },
    )
    if obs.empty:
        LOG.info("No neighbors found for %s at %s", station, row["valid"])
        return
    # 1. If this value is within the observed range, we are good.
    if obs[varname].min() <= row[varname] <= obs[varname].max():
        LOG.info("value: %s found within obs range, good", row[varname])
        return
    obs_minval = obs[varname].min()
    obs_maxval = obs[varname].max()
    outside = max(obs_minval - row[varname], row[varname] - obs_maxval)
    autozap = autozap or outside > (obs_maxval - obs_minval)
    LOG.info(
        "Value: %.2f %s outside of [%s-%s] %s",
        row[varname],
        row["valid"],
        obs_minval,
        obs_maxval,
        "Manual Review" if not autozap else "AutoZap",
    )
    if not autozap:
        res = input("Cull (y/[n]): ")
        if res != "y":
            return
    tzinfo = ZoneInfo(nt.sts[station]["tzname"])

    # Zap entry
    table = f"t{row['valid'].year}"
    conn.execute(
        sql_helper(
            "UPDATE {table} SET {varname} = null, editable = 'f' "
            "WHERE station = :station and valid = :dt",
            varname=varname,
            table=table,
        ),
        {
            "station": station,
            "dt": row["valid"],
        },
    )
    print(f"Setting ASOS {row['valid']} {varname} = null")

    if varname == "feel":
        tocull = "max_feel = null, min_feel = null, avg_feel = null"
    elif varname == "tmpf":
        tocull = "max_tmpf = null, min_tmpf = null"
    elif varname == "dwpf":
        tocull = "max_dwpf = null, min_dwpf = null"
    elif varname == "rh":
        tocull = "max_rh = null, min_rh = null, avg_rh = null"
    else:
        raise ValueError(f"Need {varname} defined here...")

    iempgconn, iemcursor = get_dbconnc("iem")
    iemcursor.execute(
        f"update summary_{row['valid'].year} set {tocull} "
        "where iemid = %s and day = %s",
        (
            nt.sts[station]["iemid"],
            row["valid"].astimezone(tzinfo).date(),
        ),
    )
    iemcursor.close()
    iempgconn.commit()
    conn.commit()


@with_sqlalchemy_conn("mesosite")
def find_neighbors(
    station: str, lon: float, lat: float, conn: Connection | None = None
) -> pd.DataFrame:
    """Find neighboring stations."""
    return pd.read_sql(
        sql_helper("""
        select id as station, ST_Distance(geom, ST_Point(:lon, :lat, 4326))
        as dist from stations where id != :station and
        archive_begin < '1981-01-01' and network ~* 'ASOS'
        and ST_Distance(geom, ST_Point(:lon, :lat, 4326)) < 2
        order by dist asc
                   """),
        conn,
        index_col="station",
        params={
            "lon": lon,
            "lat": lat,
            "station": station,
        },
    )


@click.command()
@click.option("--station", required=True)
@click.option("--network", required=True)
@click.option("--varname", default="feel")
@click.option("--ascending", is_flag=True, help="Sort ascending")
@click.option("--autozap", is_flag=True, help="Zap em all")
@click.option("--year", type=int, help="Year to filter on")
@click.option("--month", type=int, help="Month to filter on")
def main(
    station: str,
    network: str,
    varname: str,
    ascending: bool,
    autozap: bool,
    year: int | None,
    month: int | None,
):
    """Go Main Go."""
    nt = NetworkTable(network, only_online=False)
    neighbors = find_neighbors(
        station, nt.sts[station]["lon"], nt.sts[station]["lat"]
    )
    if neighbors.empty:
        LOG.warning("No neighbors found, abort!")
        return
    tbl = f"t{year}" if year is not None else "alldata"
    mfilter = ""
    if month is not None:
        mfilter = " and extract(month from valid) = :month "
    with get_sqlalchemy_conn("asos") as conn:
        obs = pd.read_sql(
            sql_helper(
                """
            select valid, {varname} from {tbl}
            where station = :station and {varname} is not null {mfilter}
            ORDER by {varname} {sortdir} LIMIT 20
                """,
                varname=varname,
                tbl=tbl,
                mfilter=mfilter,
                sortdir="asc" if ascending else "desc",
            ),
            conn,
            params={
                "station": station,
                "month": month,
            },
        )
        LOG.info("Found %s rows", len(obs.index))

        for _, row in obs.iterrows():
            process(conn, row, station, nt, varname, neighbors, autozap)


if __name__ == "__main__":
    main()
