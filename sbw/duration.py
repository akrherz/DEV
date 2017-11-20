"""SBW Intersection"""
from __future__ import print_function

import numpy as np
import tqdm
import matplotlib.pyplot as plt
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn
from pyiem.network import Table as NetworkTable


def main():
    """Go Main Go"""
    # wfo = argv[1]
    pgconn = get_dbconn('postgis')
    df = read_sql("""
        select extract(year from issue) as year,
        avg(init_expire - issue) as duration from sbw where phenomena = 'TO'
        and status = 'NEW' GROUP by year ORDER by year
    """, pgconn, index_col='year')
    (fig, ax) = plt.subplots(1, 1)
    vals = df['duration'] / np.timedelta64(1, 's')
    print(vals)
    ax.bar(df.index.values, vals / 60.)
    ax.set_ylim(34, 43)
    ax.set_ylabel("Average Warning Duration at Issuance [minutes]")
    ax.set_title("Average NWS Tornado Warning Duration at Issuance")
    fig.text(0.01, 0.01, "@akrherz 20 Nov 2017")
    ax.grid(True)
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
