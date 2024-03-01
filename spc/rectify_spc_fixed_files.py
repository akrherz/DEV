"""SPC kindly provided me an archive of their manually fixed PTS.

These files need some further help to make them noaaportish.
"""

import glob
import subprocess

from pyiem.nws.product import TextProduct
from pyiem.util import get_dbconn, logger

LOG = logger()


def process(cursor, fn):
    """Process this filename."""
    pil = fn.split("/")[1][4:10]
    # Add some filler at the top, which should get ignored?
    with open(fn, encoding="utf-8") as fh:
        newtext = fh.read()
    data = "000 \nSAUS22 KWNS 010000\n" + newtext
    prod = TextProduct(data)
    LOG.info("%s, %s, %s", fn, pil, prod.valid)
    cursor.execute(
        "SELECT data from products where pil = %s and entered = %s",
        (pil, prod.valid),
    )
    if cursor.rowcount == 0:
        LOG.info("Failed to find this product in AFOS database, skipping")
        return
    orig = cursor.fetchone()[0].replace("\r", "").strip()
    needed = orig.split("\n")[1:3]
    needed.extend([pil, ""])
    assert len(needed[1]) == 18
    newtext = "\n".join(needed) + newtext
    tmpfn = f"/tmp/{prod.get_product_id()}.txt"
    with open(tmpfn, "w", encoding="utf-8") as fh:
        fh.write(newtext)
    cmd = f"python ~/projects/pyWWA/util/make_text_noaaportish.py {tmpfn}"
    subprocess.call(cmd, shell=True)
    cmd = (
        f"cat {tmpfn} | python ~/projects/pyWWA/parsers/afos_dump.py -r -x "
        f"-u {prod.valid:%Y-%m-%dT%H:%MZ}"
    )
    subprocess.call(cmd, shell=True)
    cmd = f"cat {tmpfn} | python ~/projects/pyWWA/parsers/spc_parser.py -x "
    subprocess.call(cmd, shell=True)


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    for fn in glob.glob("fixed/KWNS*"):
        process(cursor, fn)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
