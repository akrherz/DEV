"""Fetch NEXRAD from Unidata to repair IEM holes"""
import glob
import os
import re
import datetime

from tqdm import tqdm
import requests
from pyiem.network import Table as NetworkTable
from pyiem.util import exponential_backoff

TWDR = NetworkTable("TWDR")
FNREGEX = re.compile(("\"Level3_(?P<nexrad>...)_(?P<nids>...)_"
                      "(?P<date>[0-9]{8})_(?P<time>[0-9]{4}).nids"))
DATES = [datetime.date(2018, 5, 18), datetime.date(2018, 5, 19)]


def main():
    """Go Main Go"""
    os.chdir('data/nexrad/NIDS')
    for nexrad in tqdm(glob.glob('???')):
        source = "twdr" if nexrad in TWDR.sts else "nexrad"
        os.chdir(nexrad)
        for nids in ['N0Q', 'NET', 'N0R', 'EET']:
            if not os.path.isdir(nids):
                continue
            os.chdir(nids)
            for date in DATES:
                dir_uri = date.strftime(("http://motherlode.ucar.edu/native/"
                                         "radar/level3/" + source +
                                         "/" + nids + "/" +
                                         nexrad + "/%Y%m%d/"))
                req = exponential_backoff(requests.get, dir_uri, timeout=30)
                tokens = FNREGEX.findall(req.content.decode('ascii'))
                for token in tokens:
                    localfn = "%s_%s_%s" % (token[1], token[2], token[3])
                    if os.path.isfile(localfn):
                        continue
                    remotefn = ("%sLevel3_%s_%s_%s_%s.nids"
                                ) % (dir_uri, *token)
                    req = exponential_backoff(requests.get, remotefn,
                                              timeout=30)
                    fp = open(localfn, 'wb')
                    fp.write(req.content)
                    fp.close()
                    # write files for re-ingest by Ridge
                    # ICT_20180519_1030_N0U.ridge
                    ridgefn = ("/mesonet/tmp/ridge/%s_%s_%s_%s.ridge"
                               ) % (nexrad, token[2], token[3], nids)
                    fp = open(ridgefn, 'wb')
                    fp.write(req.content)
                    fp.close()

            os.chdir('..')
        os.chdir('..')


if __name__ == '__main__':
    main()
