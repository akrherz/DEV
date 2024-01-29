"""Find warnings that are likely wrong for duration."""

import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.nws.products.vtec import VTECProduct
from pyiem.util import logger, noaaport_text

LOG = logger()


def main():
    """."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            """select distinct wfo, phenomena, significance, eventid,
            extract(year from issue)::int as year, expire - issue as duration,
            tableoid::regclass as tablename
            from warnings where
            expire - issue > '100 days'::interval and length(report) > 100
            and issue > '2013-01-01' and phenomena != 'FL'
            ORDER by year, wfo, eventid asc
            """,
            conn,
        )
    LOG.info("Found %s rows", len(df.index))
    pgconn, cursor = get_dbconnc("postgis")
    for _, row in df.iterrows():
        cursor.execute(
            f"select report, svs from {row['tablename']} "
            "where wfo = %s and phenomena = %s and significance = %s and "
            "eventid = %s",
            (
                row["wfo"],
                row["phenomena"],
                row["significance"],
                row["eventid"],
            ),
        )
        prods = []
        for row2 in cursor:
            text = noaaport_text(row2["report"])
            if text not in prods:
                prods.append(text)
            if row2["svs"] is not None:
                for svs in row2["svs"].split("__"):
                    if len(svs) < 50:
                        continue
                    svs = noaaport_text(svs)
                    if svs not in prods:
                        prods.append(svs)
        # Check 1, see if our VTEC is isolated
        good = f"{row['phenomena']}.{row['significance']}.{row['eventid']}"
        prodobjs = []
        for text in prods:
            prod = VTECProduct(text)
            prod.utcnow = prod.valid
            if not prodobjs:
                prodobjs.append(prod)
            else:
                for i, p in enumerate(prodobjs):
                    if p.valid > prod.valid:
                        prodobjs.insert(i, prod)
                        break
                else:
                    prodobjs.append(prod)
            for seg in prod.segments:
                cull = []
                for vtec in seg.vtec:
                    key = f"{vtec.phenomena}.{vtec.significance}.{vtec.etn}"
                    if key != good:
                        cull.append(vtec)
                        print(
                            f"CULL:{prod.get_product_id()} {key} {vtec} {good}"
                        )
                for vtec in cull:
                    seg.vtec.remove(vtec)
        for prod in prodobjs:
            print(prod.valid, prod.get_product_id())
        if input("Are we ready? y/[n]") == "y":
            cursor.execute(
                f"delete from {row['tablename']} where "
                "wfo = %s and phenomena = %s and significance = %s and "
                "eventid = %s",
                (
                    row["wfo"],
                    row["phenomena"],
                    row["significance"],
                    row["eventid"],
                ),
            )
            print(f"Removed {cursor.rowcount} rows")
            for prod in prodobjs:
                print(prod.get_product_id())
                prod.sql(cursor)
                for w in prod.warnings:
                    if w.find("2024-") > -1:
                        print(w)
                        print("-----------WTF")
                        return
            cursor.execute(
                "SELECT ugc, issue, expire, expire - issue as duration "
                f"from {row['tablename']} where "
                "wfo = %s and phenomena = %s and significance = %s and "
                "eventid = %s order by duration asc",
                (
                    row["wfo"],
                    row["phenomena"],
                    row["significance"],
                    row["eventid"],
                ),
            )
            for row2 in cursor:
                print(
                    f"{row2['ugc']} {row2['issue']:%Y%m%d%H%M} "
                    f"{row2['expire']:%Y%m%d%H%M} {row2['duration']}"
                )
            if input("Are we still happy? y/[n]") == "y":
                print("commit")
                cursor.close()
                pgconn.commit()
                pgconn.close()

        return


if __name__ == "__main__":
    main()
