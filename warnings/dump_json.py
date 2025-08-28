"""I write things for folks."""

from pandas.io.sql import read_sql
from pyiem.database import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        """
        SELECT row_number() OVER () as id,
        wfo as issuing_wfo,
        to_char(issue, 'YYYY-mm-dd') as startdate,
        to_char(expire, 'YYYY-mm-dd') as endate,
        ugc,
        report as forecast_blob from warnings where phenomena = 'FW'
        and significance = 'W'
    """,
        pgconn,
    )

    df.to_json("fire_weather.json", orient="records")


if __name__ == "__main__":
    main()
