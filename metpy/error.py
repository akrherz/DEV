"""
https://github.com/Unidata/MetPy/discussions/3375
"""

import numpy as np

import pandas as pd
from metpy.calc import wind_components
from metpy.units import units

pd.set_option("future.no_silent_downcasting", True)
df = (
    pd.DataFrame(
        {
            "sknt": pd.Series([1, 2, 3, None], dtype=object),
            "drct": pd.Series([4, 6, 7, None], dtype=object),
        }
    )
    .fillna(np.nan)
    .infer_objects()
)


print(
    wind_components(
        units("knot") * df["sknt"].values,
        units("degree") * df["drct"].values,
    )
)
