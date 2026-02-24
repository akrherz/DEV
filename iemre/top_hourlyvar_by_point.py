"""Find our extremes and missing data too!"""

from pathlib import Path

import click
import numpy as np
import pandas as pd
from pyiem.grid.nav import get_nav
from pyiem.iemre import get_hourly_ncname
from pyiem.util import ncopen, utc
from tqdm import tqdm


@click.command()
@click.option("--lat", type=float, default=40.0, help="Latitude")
@click.option("--lon", type=float, default=-95.0, help="Longitude")
@click.option("--varname", type=str, default="speed")
@click.option("--force", is_flag=True, help="Regenerate always")
def main(lon: float, lat: float, varname: str, force: bool):
    """Go Main Go."""
    i, j = get_nav("IEMRE", "conus").find_ij(lon, lat)
    csvfn = f"top_{varname}_by_point_{lon:.2f}_{lat:.2f}.csv"
    if force or not Path(csvfn).exists():
        progress = tqdm(range(2007, 2027))
        dfs = []
        for year in progress:
            progress.set_description(f"{year}")
            times = pd.date_range(
                f"{year}/01/01", f"{year}/12/31 23:00", freq="1h"
            ).tz_localize("UTC")
            with ncopen(get_hourly_ncname(year)) as nc:
                if varname == "speed":
                    uwnd = nc.variables["uwnd"][:, j, i]
                    vwnd = nc.variables["vwnd"][:, j, i]
                    vals = np.sqrt(uwnd**2 + vwnd**2)
                else:
                    vals = nc.variables[varname][:, j, i]
            dfs.append(pd.DataFrame({varname: vals}, index=times))

        df = pd.concat(dfs)
        df = df.loc[: pd.Timestamp(utc())]
        df.to_csv(csvfn)

    obs = pd.read_csv(csvfn, index_col=0, parse_dates=True)
    # Look for missing data where there should not be!
    print(obs.loc[obs[varname].isna()].head(20))
    obs = obs.dropna()
    print(obs.sort_values(varname, ascending=False).head())
    print(obs.sort_values(varname, ascending=True).head())


if __name__ == "__main__":
    main()
