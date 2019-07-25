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


def repair(pgconn, df):
    """Make the repairs."""
    cursor = pgconn.cursor()
    count = 0
    for _, row in tqdm(df.iterrows()):
        cursor.execute("""
            UPDATE current_log
            SET feel = %s where iemid = %s and valid = %s
        """, (row['calc_heat'], row['iemid'], row['valid']))
        count += 1
    cursor.close()
    pgconn.commit()
    return count


def main(argv):
    """Go Main Go."""
    pgconn = get_dbconn('iem')
    df = read_sql("""
            SELECT valid, iemid, tmpf, relh, feel from current_log
            WHERE tmpf > 70
            and relh is not null
        """, pgconn)
    df['calc_heat'] = heat_index(
            df['tmpf'].values * units.degF, df['relh'].values * units.percent)
    df2 = df[(df['calc_heat'] - df['feel']).abs() > 1]
    print(repair(pgconn, df2))


if __name__ == '__main__':
    main(sys.argv)
