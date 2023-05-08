"""Ingest old AFOS data!"""
import re
import sys
from datetime import datetime, timedelta, timezone

from psycopg2.extras import DictCursor

from pandas.io.sql import read_sql
from pyiem.nws.products.vtec import parser
from pyiem.nws.vtec import VTEC
from pyiem.util import get_dbconn

FMT = "%y%m%dT%H%MZ"
UNTIL = re.compile(
    r" (UNTIL|EXPIRE AT|TIL) ([0-9]+):?([0-5][0-9])? (AM|PM) ([A-Z]+)"
)
UNTIL2 = re.compile(r" (UNTIL|TIL|EXPIRE AT|THROUGH) ([0-9].*?)\.* ")


def compute_until(v):
    """Figure out when this event ends!"""
    # Attempt to figure out the UNTIL time.
    tokens = UNTIL.findall(v.unixtext.replace("\n", " "))
    # print(tokens)
    if tokens:
        tokens = tokens[0]
        # [('1015', '', 'AM', 'AST')]
        # [('12', '15', 'PM', 'AST')]
        if len(tokens[1]) > 2:
            hr = int(tokens[1][:-2])
            mi = int(tokens[1][-2:])
        else:
            hr = int(tokens[1])
            mi = 0
        ampm = tokens[3]
    else:
        tokens = UNTIL2.findall(v.unixtext.replace("\n", " "))
        # print(tokens)
        if not tokens:
            # These are generally misfire/test products, just deep6 for now
            return None
        text = tokens[0][1]
        if text.find("NOON") > -1:
            hr = 12
            mi = 0
            ampm = "PM"
        elif text.find("MIDNIGHT") > -1:
            hr = 12
            mi = 0
            ampm = "AM"
        else:
            ampm = "AM" if text.find("AM") > -1 else "PM"
            numbers = re.findall(r"\d+", text)
            if len(numbers[0]) > 2:
                hr = int(numbers[0][:-2])
                mi = int(numbers[0][-2:])
            else:
                hr = int(numbers[0])
                mi = 0
    if hr > 12:
        hr -= 12
    # If we don't know the timezone, bail with the UGC end time
    if v.tz is None:
        return v.segments[0].ugcexpire
    # Okay, we have done all we can here.
    localtime = v.valid.astimezone(v.tz)
    tstring = localtime.strftime("%Y-%m-%d ") + f"{hr}:{mi} {ampm}"
    ut = datetime.strptime(tstring, "%Y-%m-%d %I:%M %p")
    if ut.hour < localtime.hour:
        ut += timedelta(hours=24)
    return localtime.replace(
        year=ut.year,
        month=ut.month,
        day=ut.day,
        hour=ut.hour,
        minute=ut.minute,
    ).astimezone(timezone.utc)


def create_event(dbconn, v, endts):
    """Create an event!"""
    cursor = dbconn.cursor(cursor_factory=DictCursor)
    cursor.execute(
        f"SELECT max(eventid) + 1 from warnings_{v.valid.year} "
        "where phenomena = 'FF' and significance = 'W' and wfo = %s",
        (v.source[1:],),
    )
    newetn = cursor.fetchone()[0]
    if newetn is None:
        newetn = 1

    # Need to hack the VTEC into the object
    v.segments[0].vtec.append(
        VTEC(
            [
                "",
                "O",
                "NEW",
                v.source,
                "FF",
                "W",
                newetn,
                v.valid.strftime(FMT),
                endts.strftime(FMT),
            ]
        )
    )
    v.segments[0].vtec[0].year = v.valid.year
    v.sql(cursor)
    print(f"{v.segments[0].vtec[0].get_id(None)} {v.valid} {endts}")
    cursor.close()
    dbconn.commit()
    res = []
    for ugc in v.segments[0].ugcs:
        res.append(
            {
                "ugc": str(ugc),
                "wfo": v.source[1:],
                "eventid": newetn,
                "issue": v.valid,
                "expire": endts,
            }
        )
    return res


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    afosdb = get_dbconn("afos")
    postgisdb = get_dbconn("postgis")

    events = read_sql(
        "SELECT ugc, wfo, eventid, issue, expire "
        f"from warnings_{year} "
        "WHERE phenomena = 'FF' and significance = 'W' "
        "ORDER by wfo, eventid",
        postgisdb,
        index_col=None,
    )
    cursor = afosdb.cursor()
    cursor.execute(
        "SELECT data, entered from products where substr(pil, 1, 3) = 'FFW' "
        f"and entered > '{year}-01-01' and entered < '{year + 1}-01-01' "
        " and (data ~* 'FLASH FLOOD EMERGENCY' or "
        "data ~* 'FLASH FLOOD WARNING') "
        "ORDER by entered ASC"
    )
    for row in cursor:
        if row[0].find("TEST FLASH FLOOD WARNING") > -1:
            continue
        if row[0].find("TEST TEST") > -1:
            continue
        try:
            v = parser(row[0], utcnow=row[1])
            endts = compute_until(v)
        except Exception as exp:
            print(exp)
            continue
        if endts is None:
            print(f"Missing endts {v.get_product_id()}")
            continue
        # Significant dedup work already happended within the AFOS database,
        # so here we are really trying hard not to have true duplicates or
        # slight issuance time modifications.
        misses = []
        for ugc in v.segments[0].ugcs:
            df = events[
                (events["ugc"] == str(ugc))
                & (events["issue"] - timedelta(minutes=30) <= v.valid)
                & (events["expire"] == endts)
            ]
            misses.append(df.empty)
        if any(misses):
            res = create_event(postgisdb, v, endts)
            if res is None:
                continue
            # Add event to events so to prevent susequent dups
            events = events.append(res)


if __name__ == "__main__":
    main(sys.argv)
