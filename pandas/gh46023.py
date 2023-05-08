"""
https://github.com/pandas-dev/pandas/issues/46023
"""
import os
import subprocess

import pandas as pd

# Get process id of the current process
pid = os.getpid()

subprocess.call(f"lsof -p {pid} | grep postgres", shell=True)
print("running read_sql")
pd.read_sql("select 1", "postgresql://localhost/akrherz")

subprocess.call(f"lsof -p {pid} | grep postgres", shell=True)
