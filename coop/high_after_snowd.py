"""High temp after snow cover of depth"""

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn('coop')
    df = read_sql("""
    WITH data as (
        SELECT snowd, lead(high) OVER (ORDER by day ASC) as nextday
        from alldata_ia
        WHERE station = 'IA0200')
    select * from data where snowd >= 0.1 and snowd < 18
    """, pgconn, index_col=None)
    df['cat'] = (df['snowd'] / 2).astype(int)
    print(df)
    (fig, ax) = plt.subplots(1, 1)
    df.boxplot(column='nextday', by='cat', ax=ax)
    ax.set_xticks(range(1, 10))
    ax.set_xticklabels(['Trace-2', '2-4', '4-6', '6-8', '8-10', '10-12',
                        '12-14', '14-16', '16-18'])
    ax.axhline(43, color='r')
    ax.text(9.5, 43, r"43$^\circ$F", color='r')
    ax.set_xlabel("Reported Snow Depth [inch], n=%.0f" % (len(df.index), ))
    ax.set_ylabel(r"Next Day High Temperature [$^\circ$F]")
    plt.suptitle('')
    ax.set_title(("[IA0200] Ames Snow Depth and Next Day High Temperature\n"
                  r"boxes are inner quartile range, whiskers are 1.5 $\sigma$"))
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
