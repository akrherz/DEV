"""Look for missed PTS products."""
import subprocess

import requests

# third party
from tqdm import tqdm

from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    postgis_pgconn = get_dbconn("postgis")
    pcursor = postgis_pgconn.cursor()
    pcursor.execute(
        "select product_id, st_area(geom) as area, updated from spc_outlooks "
        "where updated < '2021-07-07' and geom is not null and day = 3 and "
        "threshold = 'SLGT' "
        "ORDER by area DESC LIMIT 50"
    )
    progress = tqdm(pcursor, total=pcursor.rowcount)
    for row in progress:
        product_id = row[0]
        progress.set_description(product_id)
        req = requests.get(
            f"http://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
        )
        tmpfn = f"/tmp/{product_id}.txt"
        with open(tmpfn, "wb") as fh:
            fh.write(req.content)
        cmd = f"python ~/projects/pyWWA/util/make_text_noaaportish.py {tmpfn}"
        subprocess.call(cmd, shell=True)
        cmd = (
            f"cat {tmpfn} | python ~/projects/pyWWA/parsers/spc_parser.py -x "
        )
        subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()
