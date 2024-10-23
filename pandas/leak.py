"""example leak.

https://github.com/pandas-dev/pandas/issues/57039
"""

import numpy as np
import pandas as pd

pcp = np.ones((2700, 6100), dtype=np.float64)
pcp[pcp < 0] = np.nan

for _ in range(1000):
    pd.read_csv("example.txt", engine="c")
