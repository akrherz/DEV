"""Significant Life Choice being made here, add BBB to database + text.

We have a problem with duplicated metadata in the AFOS database, this makes
canonical references from other tables not possible. This script will add
the BBB metadata to the database, and then update the AFOS table with the
newly created BBB ID.

- [ ] Add BBB value to the AFOS table
- [ ] Edit the product, adding the BBB value there
- [ ] Inspect each product, figuring out the VTEC event associated with it
- [ ] Update postgis warnings/sbw tables with product_id values

"""

import sys
from datetime import timezone

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.products.vtec import parser
from pyiem.util import logger, utc
from sqlalchemy import text

LOG = logger()


def workflow(row):
    """These have a more difficult remediation."""
    if row["bbb"] is not None:
        LOG.info("Skipping %s %s %s", row["utc_valid"], row["pil"], row["bbb"])
        return
    LOG.info("Processing %s %s", row["utc_valid"], row["pil"])
    with get_sqlalchemy_conn("afos") as conn:
        res = conn.execute(
            text("""
            select ctid, tableoid::regclass as tablename, data, bbb from
            products where entered = :entered and pil = :pil and
            bbb is null
            """),
            {
                "entered": row["utc_valid"],
                "pil": row["pil"],
            },
        )
        prodrows = res.fetchall()
    prods = [
        parser(prodrows[0][2], utcnow=row["utc_valid"]),
        parser(prodrows[1][2], utcnow=row["utc_valid"]),
    ]
    if not prods[0].segments[0].vtec and not prods[1].segments[0].vtec:
        LOG.info("No VTEC found, skipping")
        return
    if prods[0].segments[0].vtec[0].status == "T":
        LOG.info("Skipping test product")
        return
    if (
        prods[0].segments[0].vtec[0].action
        != prods[1].segments[0].vtec[0].action
    ):
        LOG.info("Actions differ, skipping")
        return
    # Our first hope is that one ETN is larger than the other
    etn1 = prods[0].segments[0].vtec[0].etn
    etn2 = prods[1].segments[0].vtec[0].etn
    if etn1 == etn2:
        LOG.info(
            "FATAL ETNs are the same %s %s %s",
            etn1,
            prods[0].get_product_id(),
            prods[1].get_product_id(),
        )
        return
    rraidx = 0 if etn1 > etn2 else 1
    LOG.info("Higher ETN [%s,%s] is %s", etn1, etn2, rraidx)
    # Need to insert RRA into the text
    lines = prodrows[rraidx][2].split("\r\r\n")
    if len(lines[2]) != 18:
        print(lines[:4])
        sys.exit()
    lines[2] = lines[2] + " RRA"
    newtext = "\r\r\n".join(lines)
    oldpid = prods[rraidx].get_product_id()
    vtec = prods[rraidx].segments[0].vtec[0]
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text("""
            select ctid from sbw where vtec_year = :vtec_year and
            eventid = :eventid and phenomena = :phenomena and
            significance = :significance and wfo = :wfo and
            product_id = :product_id 
            """),
            {
                "vtec_year": prods[rraidx].valid.year,
                "eventid": vtec.etn,
                "phenomena": vtec.phenomena,
                "significance": vtec.significance,
                "wfo": vtec.office,
                "product_id": oldpid,
            },
        )
        if res.rowcount != 1:
            LOG.info("Failed to find SBW row for %s", oldpid)
            sys.exit()
        sbwctid = res.fetchone()[0]
        res = conn.execute(
            text("""
            select ctid from warnings where vtec_year = :vtec_year and
            eventid = :eventid and phenomena = :phenomena and
            significance = :significance and wfo = :wfo and
            product_ids[1] = :product_id 
            """),
            {
                "vtec_year": prods[rraidx].valid.year,
                "eventid": vtec.etn,
                "phenomena": vtec.phenomena,
                "significance": vtec.significance,
                "wfo": vtec.office,
                "product_id": oldpid,
            },
        )
        if res.rowcount == 0:
            LOG.info("Failed to find warnings row for %s", oldpid)
            sys.exit()
        warningctids = [x[0] for x in res.fetchall()]

    # here we go
    with (
        get_sqlalchemy_conn("afos") as afos,
        get_sqlalchemy_conn("postgis") as postgis,
    ):
        # update afos data and bbb fields
        res = afos.execute(
            text(f"""
            UPDATE {prodrows[rraidx][1]} SET bbb = :bbb, data = :data
            WHERE ctid = :ctid
            """),
            {"bbb": "RRA", "data": newtext, "ctid": prodrows[rraidx][0]},
        )
        if res.rowcount != 1:
            LOG.info("Failed to update afos row %s", prodrows[rraidx][0])
            sys.exit()
        res = postgis.execute(
            text("""
            UPDATE sbw SET product_id = :newpid WHERE ctid = :ctid
            and vtec_year = :vtec_year
            """),
            {
                "newpid": oldpid + "-RRA",
                "ctid": sbwctid,
                "vtec_year": prods[0].valid.year,
            },
        )
        if res.rowcount != 1:
            LOG.info("Failed to update sbw row %s", sbwctid)
            sys.exit()
        for wctid in warningctids:
            res = postgis.execute(
                text("""
                UPDATE warnings SET
                product_ids = array_replace(product_ids, :oldpid, :newpid)
                WHERE ctid = :ctid
                and vtec_year = :vtec_year
                """),
                {
                    "oldpid": oldpid,
                    "newpid": oldpid + "-RRA",
                    "ctid": wctid,
                    "vtec_year": prods[0].valid.year,
                },
            )
            if res.rowcount != 1:
                LOG.info("Failed to update warnings row %s", wctid)
                sys.exit()
        afos.commit()
        postgis.commit()

    LOG.info("Done %s -> %s-RRA", oldpid, oldpid)


@click.command()
@click.option("--year", type=int, help="Year to process")
@click.option("--pil", help="PIL (3 char) to process")
def main(year, pil):
    """Go Main Go."""
    # build a list of problematic products
    with get_sqlalchemy_conn("afos") as conn:
        products = pd.read_sql(
            text("""
            select entered at time zone 'UTC' as utc_valid,
            pil, bbb, count(*) from products where entered >= :sts and
            entered < :ets and substr(pil, 1, 3) = :pil
            GROUP by utc_valid, pil, bbb HAVING count(*) > 1
            """),
            conn,
            params={
                "sts": utc(year, 1, 1),
                "ets": utc(year + 1, 1, 1),
                "pil": pil,
            },
        )
        if products.empty:
            LOG.info("No results found!")
            return
        products["utc_valid"] = products["utc_valid"].dt.tz_localize(
            timezone.utc
        )
        LOG.info("Found %s rows to process", len(products.index))
        products["todo"] = True
        for idx, row in products.iterrows():
            if row["count"] > 2:
                LOG.info(
                    "Skipping %s %s %s",
                    row["utc_valid"],
                    row["pil"],
                    row["count"],
                )
                products.at[idx, "todo"] = False
                continue
            bbbcomp = "bbb = :bbb" if row["bbb"] is not None else "bbb is null"
            res = conn.execute(
                text(f"""
                select ctid, tableoid::regclass as tablename, data, bbb from
                products where entered = :entered and pil = :pil and
                {bbbcomp}
                """),
                {
                    "entered": row["utc_valid"],
                    "pil": row["pil"],
                    "bbb": row["bbb"],
                },
            )
            prod1row = res.fetchone()
            prod2row = res.fetchone()
            try:
                prod1 = parser(prod1row[2], utcnow=row["utc_valid"])
                pid1 = prod1.get_product_id()
                prod2 = parser(prod2row[2], utcnow=row["utc_valid"])
                pid2 = prod2.get_product_id()
            except Exception as exp:
                products.at[idx, "todo"] = False
                LOG.info("Failed to parse %s", exp)
                continue
            # Gate 1, are the product_ids the same
            if pid1 != pid2:
                LOG.info("Product IDs differ %s %s, afos update", pid1, pid2)
                for prodrow, prod in zip(
                    [prod1row, prod2row], [prod1, prod2], strict=True
                ):
                    res = conn.execute(
                        text(
                            f"""
                        UPDATE {prodrow[1]} SET bbb = :bbb WHERE ctid = :ctid
                    """
                        ),
                        {"bbb": prod.bbb, "ctid": prodrow[0]},
                    )
                    LOG.info(
                        "Updated %s row for %s",
                        res.rowcount,
                        prod.get_product_id(),
                    )
                conn.commit()
                products.at[idx, "todo"] = False

            # Gate 2, are the VTEC events the same
            if (
                prod1.is_single_action()
                and prod2.is_single_action()
                and str(prod1.segments[0].vtec[0])
                == str(prod2.segments[0].vtec[0])
                and len(prod1.segments[0].vtec) == len(prod2.segments[0].vtec)
            ):
                LOG.info(
                    "Looks like dup: %s |%s| |%s|",
                    prod1.get_product_id(),
                    repr(prod1.text[:16]),
                    repr(prod2.text[:16]),
                )
                if (
                    prod1.text[:7] == prod2.text[:7]
                    or input("Take the longer one? [y]/n") == ""
                ):
                    delrow = (
                        prod1row
                        if len(prod1.text) < len(prod2.text)
                        else prod2row
                    )
                    res = conn.execute(
                        text(
                            f"""
                        DELETE from {delrow[1]} where ctid = :ctid
                    """
                        ),
                        {"ctid": delrow[0]},
                    )
                    LOG.info("Deleted %s", res.rowcount)
                    conn.commit()
                    products.at[idx, "todo"] = False
    # Who is left
    products = products[products["todo"]]
    if products.empty:
        LOG.info("All done!")
        return
    LOG.info("Remaining %s rows to process", len(products.index))
    for _, row in products.iterrows():
        workflow(row)


if __name__ == "__main__":
    main()
