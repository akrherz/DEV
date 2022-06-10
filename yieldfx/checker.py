import netCDF4
import numpy as np
import datetime

with netCDF4.Dataset(
    "/mesonet/share/pickup/yieldfx/baseline/clim_0025_0045.tile.nc4"
) as nc:
    p = nc.variables["prcp"]
    idx0 = (datetime.date(2020, 5, 1) - datetime.date(1980, 1, 1)).days
    idx1 = (datetime.date(2020, 7, 4) - datetime.date(1980, 1, 1)).days
    for i in range(idx0, idx1):
        print(
            "%s %.4f %.4f"
            % (
                datetime.date(1980, 1, 1) + datetime.timedelta(days=i),
                np.min(p[i]),
                np.max(p[i]),
            )
        )
