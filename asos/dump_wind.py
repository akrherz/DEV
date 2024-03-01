"""Dump ASOS wind data per year."""

import sys

from tqdm import tqdm

from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor("streamer")
    cursor.execute(
        f"""
        SELECT
        to_char(valid at time zone 'UTC', 'YYYYmmddHH24MI') as utc_valid,
        id, ST_x(geom) as lon, ST_y(geom) as lat,
        sknt as wind_speed_kts, drct as wind_direction,
        gust as wind_gust_kts, peak_wind_gust as peak_wind_gust_kts,
        peak_wind_drct as peak_wind_drct,
        to_char(peak_wind_time at time zone 'UTC', 'YYYYmmddHH24MI')
          as utc_peak_wind_time,
        case when array_to_string(wxcodes, ' ') ~* 'TS' then 1 else 0 end
        from t{year} d, stations t
        WHERE t.id = d.station and (t.network ~* 'ASOS' or t.network = 'AWOS')
        and report_type in (3, 4) and country = 'US' and
        network not in ('AK_ASOS', 'HI_ASOS', 'PR_ASOS')
    """
    )
    with open("%s.csv" % (year,), "w", encoding="utf-8") as fh:
        fh.write(
            (
                "utc_valid,id,lon,lat,wind_speed_kts,wind_direction,"
                "wind_gust_kts,peak_wind_gust_kts,peak_wind_drct,"
                "utc_peak_wind_time,ts_present\n"
            )
        )
        for row in tqdm(cursor):
            fh.write(",".join([str(s) for s in row]) + "\n")


if __name__ == "__main__":
    main(sys.argv)
