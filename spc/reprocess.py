"""Look for missed PTS products."""

import subprocess
from datetime import datetime

import requests

# third party


def main():
    """Go Main Go."""
    with open("product_list.txt") as fh:
        products = [line.strip() for line in fh if line.strip()]
    for product_id in products:
        ts = datetime.strptime(product_id[:12], "%Y%m%d%H%M")
        req = requests.get(
            f"http://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
        )
        tmpfn = f"/tmp/{product_id}.txt"
        with open(tmpfn, "wb") as fh:
            fh.write(req.content)
        cmd = f"python ~/projects/pyWWA/util/make_text_noaaportish.py {tmpfn}"
        subprocess.call(cmd, shell=True)
        cmd = (
            f"cat {tmpfn} | "
            f"pywwa-parse-spc -s 10 -u {ts:%Y-%m-%dT%H:%M} -l -x "
        )
        subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()
