from datetime import date

from pyiem.iemre import daily_offset
from pyiem.util import ncopen

tidx = daily_offset(date(2013, 4, 12))

with ncopen("/mesonet/data/mrms/2013_mrms_dep.nc") as nc:
    print(f"DEP says: {nc.variables['p01d'][1, 1889, 3231]}")

with ncopen("/mesonet/data/mrms/2013_mrms_daily.nc") as nc:
    print(f"Daily says: {nc.variables['p01d'][tidx, 1889, 3231]}")
