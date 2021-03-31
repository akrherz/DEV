"""Requested check for pre-implementation of IBW for 2021."""

from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT product_id from sps_2021 where issue > 'YESTERDAY' and "
        "(max_wind_gust is not null or max_hail_size is not null)"
    )
    for row in cursor:
        LOG.info(row)

    cursor.execute(
        "SELECT wfo, windthreat, hailthreat from sbw_2021 "
        "where issue > 'YESTERDAY' and "
        "(windthreat is not null or hailthreat is not null)"
    )
    for row in cursor:
        LOG.info(row)


if __name__ == "__main__":
    main()
