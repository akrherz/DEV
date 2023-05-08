"""Special."""
import math

from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    dbconn = get_dbconn("postgis")
    cursor = dbconn.cursor()
    cursor2 = dbconn.cursor()

    cursor.execute(
        """
    SELECT date(issue), count(*) from
    (select DISTINCT issue, wfo, eventid, phenomena from warnings
    where phenomena in ('SV','TO')
    and substr(ugc,1,3) = 'IAC' and significance = 'W'
    and extract(month from issue) = 9) as foo GROUP by date ORDER by date ASC
    """
    )

    s1 = []
    d1 = []
    c1 = []
    s2 = []
    d2 = []
    c2 = []
    s3 = []
    d3 = []
    c3 = []
    for row in cursor:
        cursor2.execute(
            f"""
        select valid, height, smps, drct from
        raob_profile p JOIN raob_flights f on
        (p.fid = f.fid) where f.station in ('KOAX','KOMA','KOVN') and
        p.pressure = 500 and p.height < 7000 and smps >= 0 and
        valid = '{row[0]:%Y-%m-%d} 00:00+00'::timestamptz + '1 day'::interval
        """
        )
        row2 = cursor2.fetchone()
        if row2:
            if row[1] >= 30:
                c1.append(row[1] * 4.0)
                s1.append(row2[2] * 1.94)
                d1.append(math.radians(row2[3]))
            elif row[1] >= 10:
                c2.append(row[1] * 4.0)
                s2.append(row2[2] * 1.94)
                d2.append(math.radians(row2[3]))
            else:
                c3.append(row[1] * 4.0)
                s3.append(row2[2] * 1.94)
                d3.append(math.radians(row2[3]))

    ax = plt.subplot(111, polar=True)
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("N")
    ax.scatter(d1, s1, s=c1, c="g", edgecolor="g", label="30+")
    ax.scatter(d2, s2, s=c2, c="b", edgecolor="b", label="10-30")
    ax.scatter(d3, s3, s=c3, c="r", edgecolor="r", label="1-10")

    ax.legend(ncol=1, loc=(0.65, 0.4), title="Warning Count")
    ax.grid(True)
    ax.set_title(
        "1986-2012 September Omaha 7 PM RAOB 500 hPa\n"
        "Wind Speed [kts] and Direction on Iowa TOR+SVR Warning Days"
    )
    ax.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
    plt.tight_layout()
    plt.savefig("test.png")


if __name__ == "__main__":
    main()
