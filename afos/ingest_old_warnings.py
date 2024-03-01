"""Ingest old AFOS data!

-- Look for WFOs in 2003 with no entries compared with 2004
with t2003 as (
    select wfo, count(*) from sbw where
    issue > '2003-01-01' and issue < '2004-01-01' and phenomena = 'SV'
    group by wfo order by wfo),
t2004 as (
    select wfo, count(*) from sbw where issue > '2004-01-01'
    and issue < '2005-01-01' and phenomena = 'SV' group by wfo order by wfo)
select t.wfo, o.count, t.count from t2004 t LEFT JOIN t2003 o on
(o.wfo = t.wfo);
"""

import re
import sys
from datetime import datetime, timedelta, timezone

from psycopg2.extras import DictCursor
from sqlalchemy import text

import pandas as pd
from pyiem.nws.products.vtec import parser
from pyiem.nws.vtec import VTEC
from pyiem.util import get_dbconn, get_sqlalchemy_conn

FMT = "%y%m%dT%H%MZ"
UNTIL = re.compile(
    r" (UNTIL|EXPIRE AT|TIL) ([0-9]+):?([0-5][0-9])? (AM|PM) ([A-Z]+)"
)
UNTIL2 = re.compile(r" (UNTIL|TIL|EXPIRE AT|THROUGH) ([A-Z0-9].*?)\.* ")
SOURCES = {"SV": "SVR", "TO": "TOR", "FF": "FFW"}


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


def create_event(dbconn, v, endts, phenomena):
    """Create an event!"""
    cursor = dbconn.cursor(cursor_factory=DictCursor)
    cursor.execute(
        f"SELECT max(eventid) + 1 from warnings_{v.valid.year} "
        "where phenomena = %s and significance = %s and wfo = %s",
        (
            phenomena,
            "W",
            v.source[1:],
        ),
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
                phenomena,
                "W",
                newetn,
                v.valid.strftime(FMT),
                endts.strftime(FMT),
            ]
        )
    )
    v.segments[0].vtec[0].year = v.valid.year
    # Yikes
    v.segments[0].sbw = v.segments[1].sbw
    v.segments[0].giswkt = v.segments[1].giswkt
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
                "phenomena": phenomena,
            }
        )
    return res


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    wfo = argv[2]
    phenomena = argv[3]
    # allows for local debugging
    afosdb = get_dbconn("afos", host="172.16.170.1")
    postgisdb = get_dbconn("postgis")
    with get_sqlalchemy_conn("postgis") as conn:
        events = pd.read_sql(
            text(
                f"""
            SELECT ugc, wfo, eventid, issue, expire
            from warnings_{year}
            WHERE phenomena = :ph and
            significance = 'W' and wfo = :wfo ORDER by wfo, eventid
            """
            ),
            conn,
            params={"wfo": wfo, "ph": phenomena},
            index_col=None,
        )
    cursor = afosdb.cursor()
    cursor.execute(
        f"""
        SELECT data, entered from products
        where pil in ('{SOURCES[phenomena]}{wfo}')
        and entered > '{year}-01-01' and entered < '{year + 1}-01-01'
        ORDER by entered ASC
        """
    )
    for row in cursor:
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
            res = create_event(postgisdb, v, endts, phenomena)
            if res is None:
                continue
            # Add event to events so to prevent susequent dups
            events = pd.concat([events, pd.DataFrame(res)])


if __name__ == "__main__":
    main(sys.argv)
