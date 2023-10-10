import datetime

from siphon.simplewebservice.iastate import IAStateUpperAir

import pandas as pd
from metpy.calc import surface_based_cape_cin
from metpy.units import units

res = IAStateUpperAir.request_data(datetime.datetime(2018, 4, 7, 17), "KXMR")
# pw = precipitable_water(res['dewpoint'].values * units.degC,
# res['pressure'].values * units('hPa'))
# print(pw)
filtered = res[pd.notnull(res["dewpoint"])]
# pw = precipitable_water(filtered['dewpoint'].values * units.degC,
# filtered['pressure'].values * units('hPa'))
# print(pw)
(sbcape, sbcin) = surface_based_cape_cin(
    filtered["pressure"].values * units.hPa,
    filtered["temperature"].values * units.degC,
    filtered["dewpoint"].values * units.degC,
)
