"""Look for missed PTS products."""
import subprocess

# third party
from tqdm import tqdm
from psycopg2.extras import RealDictCursor
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    postgis_pgconn = get_dbconn("postgis")
    pcursor = postgis_pgconn.cursor()
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT entered at time zone 'UTC' as valid, pil, source, wmo, data "
        "from products where pil = 'PTSDY1' and entered > '2020-03-08' and "
        "entered < '2020-03-23' ORDER by entered ASC"
    )
    print(f"Found {cursor.rowcount}")
    for row in tqdm(cursor, total=cursor.rowcount):
        product_id = "%s-%s-%s-%s" % (
            row["valid"].strftime("%Y%m%d%H%M"),
            row["source"],
            row["wmo"],
            row["pil"],
        )
        pcursor.execute(
            "SELECT product_id from spc_outlook where product_id = %s",
            (product_id,),
        )
        if pcursor.rowcount == 1:
            continue
        print(product_id)
        tmpfn = f"/tmp/{product_id}.txt"
        with open(tmpfn, "wb") as fh:
            fh.write(row["data"].encode("utf-8"))
        cmd = f"python ~/projects/pyWWA/util/make_text_noaaportish.py {tmpfn}"
        subprocess.call(cmd, shell=True)
        cmd = (
            f"cat {tmpfn} | python ~/projects/pyWWA/parsers/spc_parser.py -x "
        )
        subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()
