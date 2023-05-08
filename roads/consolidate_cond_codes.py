"""Too many cats.

We cut down the amount of road condition combos, dropped MC into PC.

 select cond_code, max(label), count(*), min(valid), max(valid) from
 roads_log r JOIN roads_conditions c on (r.cond_code = c.code)
 GROUP by cond_code ORDER by cond_code ASC;

"""

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        "SELECT * from roads_conditions where label ~* 'MC' ORDER by code ASC",
        pgconn,
        index_col="code",
    )
    for cond_code, row in df.iterrows():
        cursor = pgconn.cursor()
        df2 = read_sql(
            "SELECT towing_prohibited, limited_vis, count(*) from roads_log "
            "WHERE cond_code = %s GROUP by towing_prohibited, limited_vis",
            pgconn,
            params=(cond_code,),
        )
        if df2.empty:
            print(f"no rows for {row}")
            cursor.execute(
                "DELETE from roads_conditions WHERE code = %s", (cond_code,)
            )
            cursor.close()
            pgconn.commit()
            continue
        print(f"--- code: {cond_code} label: {row['label']}")
        print(df2)
        res = input("skip? [y]/n")
        if res == "":
            continue
        work = []
        args = []
        new_cond_code = int(input("New code: "))
        if new_cond_code != cond_code:
            work.append("cond_code = %s")
            args.append(new_cond_code)
        res = input("hardcode towing?: y/[n]")
        if res == "y":
            work.append("towing_prohibited = %s")
            args.append(True)
        res = input("hardcode limited_vis?: y/[n]")
        if res == "y":
            work.append("limited_vis = %s")
            args.append(True)
        if not work:
            continue
        print(work, args)
        cursor.execute(
            f"UPDATE roads_log SET {','.join(work)} WHERE cond_code = %s",
            (*args, cond_code),
        )
        print("Updated %s rows" % (cursor.rowcount,))
        cursor.execute(
            "DELETE from roads_conditions WHERE code = %s", (cond_code,)
        )
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
