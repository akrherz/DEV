"""This is it.  We are attempting to rectify a 15+ year old issue."""

import sys
from datetime import timezone

import click
from ingest_old_warnings import compute_until
from sqlalchemy import text

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.product import TextProduct, TextProductException
from pyiem.util import logger, utc

LOG = logger()
PIL2PHENOM = {
    "SVR": "SV",
    "TOR": "TO",
    "FFW": "FF",
}


def print_other_warnings(prod):
    """Look for similar warnings."""
    with get_sqlalchemy_conn("postgis") as conn:
        warnings = pd.read_sql(
            text("""
    select ugc, issue at time zone 'UTC' as utc_issue,
    expire at time zone 'UTC' as utc_expire from warnings
    where vtec_year = :year and issue >= :sts and issue < :ets and
    phenomena = :phenomena and significance = 'W' and wfo = :wfo
    and ugc = ANY(:ugcs) order by ugc asc, issue asc
                 """),
            conn,
            params={
                "year": prod.valid.year,
                "sts": prod.valid - pd.Timedelta("4 hours"),
                "ets": prod.valid + pd.Timedelta("4 hours"),
                "phenomena": PIL2PHENOM[prod.afos[:3]],
                "wfo": prod.source[1:],
                "ugcs": [str(ugc) for ugc in prod.segments[0].ugcs],
            },
        )
    print("Other Warnings:")
    print(warnings)


def insert(prod, ugclist, eventid):
    """Insert a new warning into the database."""
    phenomena = PIL2PHENOM[prod.afos[:3]]
    if eventid is None:
        with get_sqlalchemy_conn("postgis") as conn:
            res = conn.execute(
                text("""
                select max(eventid) from warnings where
                vtec_year = :vtec_year and phenomena = :phenomena and
                significance = 'W' and wfo = :wfo
                 """),
                {
                    "vtec_year": prod.valid.year,
                    "phenomena": phenomena,
                    "wfo": prod.source[1:],
                },
            )
            eventid = res.fetchone()[0]
            if eventid is None:
                eventid = 1
            else:
                eventid += 1
    until = compute_until(prod)
    dur1 = (prod.segments[0].ugcexpire - prod.valid).total_seconds() / 60.0
    if until is None:
        dur2 = None
    else:
        dur2 = (until - prod.valid).total_seconds() / 60.0
    print("\n\n----------------------------------------------")
    print_other_warnings(prod)
    print(prod.text[:400])
    print(f"       UGCS: {ugclist}")
    print(f"       EVENTID: {eventid}")
    print(f"       ISSUE: {prod.valid}")
    print(f"       1.UGCEXPIRE: {prod.segments[0].ugcexpire} {dur1}")
    print(f"       2.UNTIL: {until} {dur2}")
    print(f"       WFO: {prod.source[1:]}")
    res = input("Proceed? 1/2/[n] ")
    if res in ["", "n"]:
        return None
    expire = prod.segments[0].ugcexpire if res == "1" else until
    sig = prod.get_signature()
    if sig is not None:
        sig = sig[:24]
    with get_sqlalchemy_conn("postgis") as conn:
        for ugc in ugclist:
            res = conn.execute(
                text(f"""
    INSERT into warnings (issue, expire, updated, wfo, eventid, status,
    fcster, ugc, phenomena, significance, gid, init_expire, product_issue,
    is_emergency, is_pds, purge_time, product_ids, vtec_year)
    values (:issue, :expire, :issue, :wfo, :eventid, 'NEW', :fcster, :ugc,
    :phenomena, 'W', get_gid('{ugc}', :issue), :expire, :issue, 'f', 'f',
    :expire, :pids, :vtec_year) returning gid
                """),
                {
                    "vtec_year": prod.valid.year,
                    "phenomena": phenomena,
                    "eventid": eventid,
                    "ugc": str(ugc),
                    "issue": prod.valid,
                    "expire": expire,
                    "product_ids": [prod.get_product_id()],
                    "fcster": sig,
                    "wfo": prod.source[1:],
                    "pids": [prod.get_product_id()],
                },
            )
            gid = res.fetchone()[0]
            if gid is None:
                print("Failed to insert")
                sys.exit()
        conn.commit()


def update_postgis(prod: TextProduct):
    """See what our database has, oh boy."""
    prod_id = prod.get_product_id()
    phenomena = PIL2PHENOM.get(prod.afos[:3])
    if phenomena is None:
        print(f"Unknown pil {prod_id}")
        return
    ugclist = [str(ugc) for ugc in prod.segments[0].ugcs]
    with get_sqlalchemy_conn("postgis") as conn:
        # 1. expire does not always equal ugcexpire, gasp
        warnings = pd.read_sql(
            text("""
            select ctid, ugc, product_ids, eventid from warnings
            where vtec_year = :vtec_year and
            phenomena = :phenomena and ugc = ANY(:ugcs) and
            (expire = :expire or issue = :issue) and significance = 'W'
            """),
            conn,
            params={
                "vtec_year": prod.valid.year,
                "phenomena": phenomena,
                "ugcs": ugclist,
                "issue": prod.valid,
                "expire": prod.segments[0].ugcexpire,
            },
        )
    # If no entries, start logic to insert one
    if warnings.empty:
        LOG.info(
            "No warnings found for %s %s issue: %s ugcexpire: %s",
            prod.get_product_id(),
            ugclist,
            prod.valid,
            prod.segments[0].ugcexpire,
        )
        insert(prod, ugclist, None)
        return
    missing_ugclist = [u for u in ugclist if u not in warnings.values]
    if missing_ugclist:
        eventids = warnings["eventid"].unique()
        if eventids.size == 1:
            LOG.info(
                "%s Missing UGCs: %s", prod.get_product_id(), missing_ugclist
            )
            insert(prod, missing_ugclist, eventids[0])
    sig = prod.get_signature()
    if sig is not None:
        sig = sig[:24]

    with get_sqlalchemy_conn("postgis") as conn:
        for _, row in warnings.iterrows():
            if not row["product_ids"]:
                LOG.info("assigning %s to %s", prod_id, row["ctid"])
                res = conn.execute(
                    text("""
                update warnings SET product_ids = :pids, fcster = :sig
                WHERE vtec_year = :vtec_year and
                ctid = :ctid
                """),
                    {
                        "pids": [prod.get_product_id()],
                        "sig": sig,
                        "vtec_year": prod.valid.year,
                        "ctid": row["ctid"],
                    },
                )
                if res.rowcount != 1:
                    LOG.warning("Abort: Failed to update warning!")
                    sys.exit()
                conn.commit()


def handle_afos_row(conn, row):
    """Process a single AFOS row."""
    prod = None
    try:
        prod = TextProduct(row["data"], utcnow=row["utc_valid"])
        if prod.afos is None:
            raise Exception("No AFOS")
        if prod.segments[0].ugcexpire is None:
            raise Exception("No UGC Expire")
        # This is lame, but we need to be rectified
        prod.source = row["source"]
        # Does ugcexpire make sense?
        threshold = prod.valid + pd.Timedelta("3 minutes")
        if prod.segments[0].ugcexpire <= threshold:
            newugcexpire = compute_until(prod)
            LOG.info(
                "fixing %s ugcexpire %s <= valid %s newugcexpire %s",
                prod.get_product_id(),
                prod.segments[0].ugcexpire,
                threshold,
                newugcexpire,
            )
            threshold2 = prod.valid + pd.Timedelta(minutes=120)
            if threshold < newugcexpire < threshold2:
                prod.segments[0].ugcexpire = newugcexpire
    except TextProductException as exp:
        LOG.info(
            "%s swallowed: %s",
            exp,
            row["ctid"],
        )
    except Exception as exp:
        LOG.info("%s Failed to parse product: %s", exp, row["ctid"])
        return
    if prod is None:
        return
    if abs((prod.valid - row["utc_valid"]).total_seconds()) > 3600:
        LOG.info(
            "Major delta product at %s is not valid at %s %s",
            row["utc_valid"],
            prod.valid,
            (prod.valid - row["utc_valid"]).total_seconds(),
        )
        return
    if prod.valid != row["utc_valid"]:
        LOG.info(
            "Updating %s %s -> %s",
            prod.get_product_id(),
            row["utc_valid"],
            prod.valid,
        )
        if prod.valid.month == 6 and row["utc_valid"].month == 7:
            return
        conn.execute(
            text(f"""
            UPDATE {row['table']} SET entered = :valid
            WHERE ctid = :ctid
            """),
            {"ctid": row["ctid"], "valid": prod.valid},
        )
        conn.commit()
    update_postgis(prod)


def do_date(dt):
    """Go Main Go."""
    # build a list of problematic products
    with get_sqlalchemy_conn("afos") as conn:
        products = pd.read_sql(
            text("""
            select ctid, source, entered at time zone 'UTC' as utc_valid,
            pil, bbb, data, tableoid::regclass as table
            from products where entered >= :sts and
            entered <= :ets and substr(pil, 1, 3) in ('SVR', 'FFW', 'TOR')
            and strpos(data, '...TEST...') = 0
            ORDER by entered ASC
            """),
            conn,
            params={
                "sts": utc(dt.year, dt.month, dt.day),
                "ets": utc(dt.year, dt.month, dt.day, 23, 59),
            },
        )
        if products.empty:
            LOG.info("No products found for date: %s", dt)
            return
        products["utc_valid"] = products["utc_valid"].dt.tz_localize(
            timezone.utc
        )
        for _, row in products.iterrows():
            handle_afos_row(conn, row)


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="date to process")
@click.option("--year", type=int, help="year to process")
def main(dt, year):
    """Go Main."""
    if year is not None:
        for valid in pd.date_range(f"{year}/01/01", f"{year}/12/31"):
            do_date(valid)
    else:
        do_date(dt)


if __name__ == "__main__":
    main()
