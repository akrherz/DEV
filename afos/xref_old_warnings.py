"""This is it.  We are attempting to rectify a 15+ year old issue."""

import sys
from datetime import timezone

import click
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


def insert(prod, ugc, eventid):
    """Insert a new warning into the database."""
    phenomena = PIL2PHENOM[prod.afos[:3]]
    with get_sqlalchemy_conn("postgis") as conn:
        entries = pd.read_sql(
            text("""
                select eventid, issue, expire from warnings where
                vtec_year = :vtec_year and phenomena = :phenomena and
                ugc = :ugc and significance = 'W' and issue > :sts
                and issue < :ets order by issue DESC
                 """),
            conn,
            params={
                "vtec_year": prod.valid.year,
                "phenomena": phenomena,
                "ugc": str(ugc),
                "sts": prod.valid - pd.Timedelta("1 day"),
                "ets": prod.valid + pd.Timedelta("1 day"),
            },
        )
    if not entries.empty:
        print(entries)
    return
    print(prod.text[:400])
    if input("Proceed? y/[n] ") in ["", "n"]:
        return None
    with get_sqlalchemy_conn("postgis") as conn:
        if eventid is None:
            res = conn.execute(
                text("""
                SELECT max(eventid) from warnings
                WHERE vtec_year = :vtec_year and phenomena = :phenomena
                     and significance = 'W' and wfo = :wfo
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
            LOG.info("Generating new eventid: %s", eventid)
        sig = prod.get_signature()
        if sig is not None:
            sig = sig[:24]
        res = conn.execute(
            text(f"""
            INSERT into warnings (issue, expire, updated, wfo, eventid, status,
                 fcster, ugc, phenomena, significance, gid, init_expire,
                 product_issue, is_emergency, is_pds, purge_time, product_ids,
                 vtec_year) values(:issue, :expire, :issue, :wfo, :eventid,
                 'NEW', :fcster, :ugc, :phenomena, 'W',
                 get_gid('{ugc}', :issue), :expire,
                 :issue, 'f', 'f', :expire, :pids, :vtec_year)
                returning gid
            """),
            {
                "vtec_year": prod.valid.year,
                "phenomena": phenomena,
                "eventid": eventid,
                "ugc": str(ugc),
                "issue": prod.valid,
                "expire": prod.segments[0].ugcexpire,
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
        return eventid


def update_postgis(prod: TextProduct):
    """See what our database has, oh boy."""
    phenomena = PIL2PHENOM[prod.afos[:3]]
    eventid = None
    with get_sqlalchemy_conn("postgis") as conn:
        for ugc in prod.segments[0].ugcs:
            # 1. expire does not always equal ugcexpire, gasp
            res = conn.execute(
                text("""
                select ctid, ugc, product_ids from warnings
                where vtec_year = :vtec_year and
                phenomena = :phenomena and ugc = :ugc and
                (expire = :expire or issue = :issue) and significance = 'W'
                """),
                {
                    "vtec_year": prod.valid.year,
                    "phenomena": phenomena,
                    "ugc": str(ugc),
                    "issue": prod.valid,
                    "expire": prod.segments[0].ugcexpire,
                },
            )
            if res.rowcount == 0:
                LOG.info(
                    "Failed to find warning for %s %s",
                    prod.get_product_id(),
                    ugc,
                )
                eventid = insert(prod, ugc, eventid)
                continue
            if res.rowcount > 1:
                LOG.info(
                    "Found %s warnings for %s %s",
                    res.rowcount,
                    ugc,
                    prod.get_product_id(),
                )
                return
            row = res.fetchone()
            if prod.get_product_id() in row[2]:
                continue
            if row[2]:
                print(
                    "Dup for %s %s %s %s %s"
                    % (prod.valid, ugc, prod, row[2], prod.get_product_id())
                )
                continue
            sig = prod.get_signature()
            if sig is not None:
                sig = sig[:24]
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
                    "ctid": row[0],
                },
            )
            if res.rowcount != 1:
                print("Failed to update all the warnings!")
                sys.exit()
            conn.commit()


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
            prod = None
            try:
                prod = TextProduct(row["data"], utcnow=row["utc_valid"])
                if prod.afos is None:
                    raise Exception("No AFOS")
                # This is lame, but we need to be rectified
                prod.source = row["source"]
            except TextProductException as exp:
                LOG.info(
                    "%s swallowed: %s",
                    exp,
                    row["ctid"],
                )
            except Exception as exp:
                LOG.info("%s Failed to parse product: %s", exp, row["ctid"])
                continue
            if prod is None:
                continue
            if abs((prod.valid - row["utc_valid"]).total_seconds()) > 3600:
                LOG.info(
                    "Major delta product at %s is not valid at %s %s",
                    row["utc_valid"],
                    prod.valid,
                    (prod.valid - row["utc_valid"]).total_seconds(),
                )
                continue
            if prod.valid != row["utc_valid"]:
                LOG.info(
                    "Updating %s %s -> %s",
                    prod.get_product_id(),
                    row["utc_valid"],
                    prod.valid,
                )
                conn.execute(
                    text(f"""
                    UPDATE {row['table']} SET entered = :valid
                    WHERE ctid = :ctid
                    """),
                    {"ctid": row["ctid"], "valid": prod.valid},
                )
                conn.commit()
            update_postgis(prod)


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
