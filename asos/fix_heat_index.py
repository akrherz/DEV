"""Oh the pain.

Between MetPy and my pyIEM library, neither was implementing the NWS equation
for heat index.  So here we are, repairing the damage.
"""
import sys
import datetime

from pyiem.util import get_dbconn, utc
from tqdm import tqdm
import pandas as pd
from pandas.io.sql import read_sql
from metpy.units import units
from metpy.calc.basic import heat_index


def repair(pgconn, df, table):
    """Make the repairs."""
    cursor = pgconn.cursor()
    count = 0
    for _, row in df.iterrows():
        cursor.execute("""
            UPDATE """ + table + """
            SET feel = %s where station = %s and valid = %s
        """, (row['calc_heat'], row['station'], row['valid']))
        count += 1
    cursor.close()
    pgconn.commit()
    return count


def main(argv):
    """Go Main Go."""
    pgconn = get_dbconn('asos')
    done = 0
    pbar = tqdm(pd.date_range(argv[1], argv[2]))
    for date in pbar:
        pbar.set_description(date.strftime("%Y-%m-%d"))
        sts = utc(date.year, date.month, date.day)
        ets = sts + datetime.timedelta(days=1)
        table = "t%s" % (sts.year, )
        df = read_sql("""
            SELECT valid, station, tmpf, relh, feel from """ + table + """
            WHERE valid >= %s and valid < %s and tmpf > 70
            and relh is not null
        """, pgconn, params=(sts, ets))
        df['calc_heat'] = heat_index(
            df['tmpf'].values * units.degF, df['relh'].values * units.percent)
        df2 = df[(df['calc_heat'] - df['feel']).abs() > 1]
        if df2.empty:
            continue
        done += repair(pgconn, df2, table)
    print("Turned over %s rows" % (done, ))


if __name__ == '__main__':
    main(sys.argv)
