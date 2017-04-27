"""Warning load by minute"""
import psycopg2
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pytz

TZ = pytz.timezone("America/Chicago")
PGCONN = psycopg2.connect(database='postgis', host='localhost',
                          port=5555, user='nobody')


def getp(phenomena):
    """Do Query"""
    cursor = PGCONN.cursor()
    cursor.execute("""
     WITH data as
     (SELECT t, count(*) from
     (select phenomena,
     generate_series(issue, expire, '1 minute'::interval) as t
     from sbw_2011 where status = 'NEW' and issue > '2011-04-26' and
     issue < '2011-04-29' and phenomena in %s) as foo
     GROUP by t),

     ts as (select generate_series('2011-04-26'::timestamptz,
      '2011-04-29 00:00-05'::timestamptz, '1 minute'::interval) as t)

     SELECT ts.t, data.count from ts LEFT JOIN data on (data.t = ts.t)
     ORDER by ts.t ASC
    """, (phenomena,))
    times = []
    counts = []
    for row in cursor:
        times.append(row[0])
        counts.append(row[1] if row[1] is not None else 0)

    return times, counts


def main():
    """Main"""
    to_t, to_c = getp(('TO',))
    for t, c in zip(to_t, to_c):
        if c > 40:
            print t, c

    b_t, b_c = getp(('SV', 'TO'))

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    ax.fill(b_t, b_c, zorder=1, color='teal', label='Severe TStorm + Tornado')
    ax.fill(to_t, to_c, zorder=2, color='r', label='Tornado')

    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12],
                                                  tz=TZ))
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter('%I %p\n%d %b',
                             tz=TZ))

    ax.set_title(("26-28 April 2011 National Weather Service "
                  "Storm Based Warning Load\n"
                  "At least 1 Tornado Warning active "
                  "between: 3:10 PM 26 April - 8:45 AM 28 April"))
    ax.set_ylabel("Active Warning Count")
    ax.legend(loc='best', ncol=2)
    ax.set_ylim(bottom=0.1)
    ax.set_xlim(to_t[0], to_t[-1])
    ax.set_xlabel("Central Daylight Time")
    fig.text(0.01, 0.01, "@akrherz, generated 27 Apr 2017")

    fig.savefig('test.png')


if __name__ == '__main__':
    main()
