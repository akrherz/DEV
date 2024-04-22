import subprocess

import pandas as pd

for dt in pd.date_range("1994/01/01", "1994/12/31"):
    cmd = f"python xref_old_warnings.py --date={dt:%Y-%m-%d}"
    subprocess.call(cmd, shell=True)
