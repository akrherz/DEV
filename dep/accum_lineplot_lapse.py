"""A lapse of accumulated erosion for a year."""
import calendar

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn

SCENARIOS = {
    0: 'DEP Baseline',
    36: 'Switchgrass >= 3%',
    37: 'Switchgrass >= 6%',
    38: 'Switchgrass >= 10%',
}

def gendata():
    """Generate the data we need."""
    pgconn = get_dbconn('idep')
    dates = pd.date_range('2019-01-01', '2019-12-31').strftime("%m%d")
    for scenario in [0, 36, 37, 38]:
        df = read_sql("""
        WITH data as (
            SELECT r.huc_12, to_char(valid, 'mmdd') as sday,
            sum(avg_delivery) / 10. as d from results_by_huc12 r, huc12 h
            WHERE r.huc_12 = h.huc_12 and h.scenario = 0 and h.states ~* 'IA'
            and r.scenario = %s and valid between '2008-01-01' and '2018-01-01'
            GROUP by r.huc_12, sday),
        huc_count as (
            select count(*) from huc12 WHERE scenario = 0 and states ~* 'IA'
        ),
        agg as (
            SELECT sday, sum(d) * 4.463 as data
            FROM data d, huc_count h GROUP by sday ORDER by sday
        )
        select sday, data / h.count as avg from agg a, huc_count h
        WHERE sday != '0229' ORDER by sday
        """, pgconn, params=(scenario, ), index_col='sday')
        df = df.reindex(dates).fillna(0)
        df.index.name = 'sday'
        df.to_csv('/tmp/s%s.csv' % (scenario, ), index=True)


def plot():
    """Go Plot Go."""
    dfs = {}
    for scenario in [0, 36, 37, 38]:
        dfs[scenario] = pd.read_csv(
            '/tmp/s%s.csv' % (scenario, )).set_index('sday')
        dfs[scenario]['accum'] = dfs[scenario]['avg'].cumsum()

    for i, sday in enumerate(dfs[0].index.values):
        if i == 0:
            continue
        (fig, ax) = plt.subplots(1, 1)
        for scenario in [0, 36, 37, 38]:
            df = dfs[scenario]
            ax.plot(
                range(i), df.iloc[:i]['avg'],
                label=SCENARIOS[scenario], lw=2)
        ax.set_xlim(0, 366)
        ax.set_ylim(0, 0.2)
        ax.grid(True)
        ax.legend(loc=2)
        ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305,
                       335, 365))
        ax.set_xticklabels(calendar.month_abbr[1:])
        ax.set_ylabel("Hillslope Soil Loss [T/a/day]")
        ax.set_title("2008-2017 DEP Daily Average Hillslope Soil Loss")

        fig.savefig('/tmp/frames/%05i.png' % (i - 1, ))
        plt.close()


if __name__ == '__main__':
    # gendata()
    plot()
