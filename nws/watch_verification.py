"""Crude Watch Verification."""
from datetime import timezone

from tqdm import tqdm
import geopandas as gpd
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    # Retreive a listing of watches
    # Watch number,
    # Year,
    # Hour of Issuance,
    # Watch Duration,
    df = gpd.read_postgis(
        """with tors as (
            SELECT issued at time zone 'UTC' as utc_issue,
            expired at time zone 'UTC' as utc_expire,
            extract(year from issued at time zone 'UTC') as year, num,
            geom from watches
            WHERE issued > '2005-01-01' and type = 'TOR')
        SELECT utc_issue, utc_expire, year, num, geom,
        string_agg(state_abbr, ',') as states from tors t, states s
        WHERE st_intersects(t.geom, s.the_geom) GROUP by utc_issue,
        utc_expire, year, num, geom ORDER by utc_issue ASC
        """,
        pgconn,
        index_col=None,
        geom_col="geom",
    )
    # Month,
    df["month"] = df["utc_issue"].dt.month
    # Day,
    df["day"] = df["utc_issue"].dt.day
    # Did it touch Iowa,
    df["touches_iowa"] = df["states"].apply(lambda x: x.find("IA") > -1)
    # Did it touch Oklahoma,
    df["touches_oklahoma"] = df["states"].apply(lambda x: x.find("OK") > -1)
    df["lsr_tornado_reports"] = 0
    df["tornado_warnings"] = 0
    for idx, row in tqdm(df.iterrows(), total=len(df.index)):
        # LSR Tornado Reports,
        cursor.execute(
            "SELECT distinct valid, geom from lsrs WHERE valid >= %s and "
            "valid < %s and typetext = 'TORNADO' and "
            "ST_Contains(ST_SetSRID(ST_GeomFromEWKT(%s), 4326), geom)",
            (
                row["utc_issue"].replace(tzinfo=timezone.utc),
                row["utc_expire"].replace(tzinfo=timezone.utc),
                row["geom"].wkt,
            ),
        )
        df.at[idx, "lsr_tornado_reports"] = cursor.rowcount
        # NWS Tornado Warnings Issued
        cursor.execute(
            "SELECT wfo, eventid from sbw WHERE issue >= %s and "
            "issue < %s and phenomena = 'TO' and significance = 'W' and "
            "status = 'NEW' and "
            "ST_Intersects(ST_SetSRID(ST_GeomFromEWKT(%s), 4326), geom)",
            (
                row["utc_issue"].replace(tzinfo=timezone.utc),
                row["utc_expire"].replace(tzinfo=timezone.utc),
                row["geom"].wkt,
            ),
        )
        df.at[idx, "tornado_warnings"] = cursor.rowcount
    df = df.drop("geom", axis=1)
    df.to_csv("watch_verification.csv", index=False)


if __name__ == "__main__":
    main()
