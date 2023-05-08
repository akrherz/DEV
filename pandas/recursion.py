"""Pandas 1.2.0 bug."""
from datetime import datetime, timezone

import pandas as pd

df = pd.DataFrame(range(31))
df["dt"] = pd.date_range("2020/12/01", "2020/12/31", tz="UTC")
df["dt"].iloc[5] = pd.NaT
df["dt"] = df["dt"].fillna(datetime(1980, 1, 1, tzinfo=timezone.utc))
