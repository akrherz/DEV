"""Add variable to climatology dataset."""

from pyiem.iemre import get_dailyc_ncname
from pyiem.util import ncopen


def main():
    """Go Main."""
    with ncopen(get_dailyc_ncname(), "a") as nc:
        v = nc.createVariable(
            "swdn", float, ("time", "lat", "lon"), fill_value=1.0e20
        )
        v.units = "MJ d-1"
        v.long_name = "All Sky Insolation Incident on a Horizontal Surface"
        v.standard_name = "All Sky Insolation Incident on a Horizontal Surface"
        v.coordinates = "lon lat"
        v.description = "Averaged from 1979-2022 MERRA"


if __name__ == "__main__":
    main()
