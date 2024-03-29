"""Send *cough* real-traffic to iemvs webhost."""

import re
import sys
import warnings
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

import requests
from tqdm import tqdm
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter("ignore", InsecureRequestWarning)
IPADDR = sys.argv[1]
IGNORE = re.compile("^/(c|cache|archive|data)/")


def fetch(url, ans):
    """Go get it."""
    if IGNORE.match(url):
        return
    req = requests.get(
        f"https://{IPADDR}{url}",
        headers={"Host": "mesonet.agron.iastate.edu"},
        verify=False,
        timeout=60,
    )
    # 503 is server too busy
    if req.status_code == 503:
        return
    if req.status_code != ans and ans not in [302, 500]:
        print(f"{url} GOT {req.status_code} not {ans}")


def main():
    """Go Main Go..."""
    futures = set()
    progress = tqdm()
    with open("iem.log", encoding="utf-8") as fh:
        with ThreadPoolExecutor(max_workers=16) as executor:
            for line in fh:
                tokens = line.split()
                progress.update(1)
                if len(futures) >= 1000:
                    completed, futures = wait(
                        futures, return_when=FIRST_COMPLETED
                    )
                futures.add(executor.submit(fetch, tokens[6], int(tokens[8])))


if __name__ == "__main__":
    main()
