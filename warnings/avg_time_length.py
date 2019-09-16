"""Length of warnings."""

import numpy as np
from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.nws.vtec import VTEC_PHENOMENA
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    pgconn = get_dbconn('postgis')
    (fig, ax) = plt.subplots(1, 1)
    df = read_sql("""
        select extract(year from issue)::int as year, phenomena,
        extract(epoch from avg(init_expire - issue)) as duration,
        avg(ST_area(geom::geography)) / 1000000. as area
        from sbw WHERE
        phenomena in ('FF') and significance = 'W' and status = 'NEW'
        and issue > '2008-01-01'
        GROUP by year, phenomena ORDER by year ASC
    """, pgconn, index_col='year')
    for phenom in df['phenomena'].unique():
        df2 = df[df['phenomena'] == phenom]
        ax.plot(
            df2.index.values, df2['duration'].values,
            label=VTEC_PHENOMENA[phenom], lw=2)
    ax.set_xticks(range(2008, 2020, 2))
    # ax.set_yticks(np.arange(30, 60, 5) * 60.)
    # ax.set_yticklabels(np.arange(30, 60, 5, dtype='i'))
    # ax.set_ylabel("Warning Duration at Issuance (minutes)")
    ax.set_yticks(np.arange(150, 271, 15) * 60.)
    ax.set_yticklabels(
        ["%.2f" % (x, ) for x in np.arange(150, 271, 15) / 60.])
    ax.set_ylabel("Warning Duration at Issuance (hours)")
    # ax.set_ylabel(
    # "Time Duration normalized by polygon size (seconds / sq km)")
    ax.set_title("NWS Average Warning Time Duration by Year")
    ax.set_xlabel("2019 thru 15 Sept 2019, based on unofficial IEM archives.")
    ax.grid(True)
    ax.legend(loc=2)
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
