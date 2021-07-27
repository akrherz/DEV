"""Requested check for pre-implementation of IBW for 2021."""

from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT product_id from sps_2021 where issue > 'YESTERDAY' and "
        "max_wind_gust is null and max_hail_size is null"
    )
    LOG.info("SPS products without the new IBW tags")
    for row in cursor:
        LOG.info(row[0])

    cursor.execute(
        "SELECT distinct wfo from sbw_2021 "
        "where phenomena = 'SV' and issue > 'YESTERDAY' and "
        "windthreat is null and hailthreat is null"
    )
    LOG.info("SVR Products from WFOs without the new tags")
    for row in cursor:
        LOG.info(row[0])


if __name__ == "__main__":
    main()
