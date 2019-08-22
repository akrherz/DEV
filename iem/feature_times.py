"""Feature analysis."""
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql
import numpy as np
from scipy import stats


def main():
    """GO Main Go."""
    pgconn = get_dbconn("mesosite")

    df = read_sql("""
        SELECT valid, good, bad, abstain,
        extract(hour from valid) as hour,
        extract(minute from valid) as minute from feature
        ORDER by valid
    """, pgconn, index_col='valid')
    df['minutes'] = df['hour'] * 60 + df['minute']
    df['total'] = df['good'] + df['bad'] + df['abstain']
    df['favorable'] = df['good'] / df['total'] * 100.

    (fig, ax) = plt.subplots(2, 1, sharex=True)

    ax[0].scatter(df.index.values, df['minutes'].values)
    ax[0].set_ylim(0, 24*60)
    ax[0].set_yticks(np.arange(0, 8) * 180)
    ax[0].set_yticklabels(
        ['Mid', '3 AM', '6 AM', '9 AM', 'Noon', '3 PM', '6 PM', '9 PM'])
    ax[0].set_title(("4,500 IEM Daily Features :: %s - 21 Aug 2019"
                     ) % (df.index.values[0].strftime("%-d %b %Y")))
    ax[0].grid(True)
    ax[0].set_ylabel("Posted Time")

    ax[1].scatter(
        df.index.values, df['favorable'].values, color='b', label="Good")
    # ax[1].scatter(dates2, abstain, color='tan', label="Abstain")
    ax[1].set_ylim(0, 100)
    ax[1].grid(True)
    ax[1].set_ylabel("Good Votes (Percent of Total)")
    ax[1].set_xlim(df.index.values[0], df.index.values[-1])
    ax[1].set_xlabel((
        "Total Votes; Good: %s (%.1f%%) Bad: %s (%.1f%%) Abstain: %s (%.1f%%)"
    ) % (
        df['good'].sum(), df['good'].sum() / df['total'].sum() * 100.,
        df['bad'].sum(), df['bad'].sum() / df['total'].sum() * 100.,
        df['abstain'].sum(), df['abstain'].sum() / df['total'].sum() * 100.
    ))

    fig.savefig('test.png')


if __name__ == '__main__':
    main()
