"""Plot some NOHRSC stuff.

https://www.nohrsc.noaa.gov/archived_data/instructions.html
gdal_translate  us_ssmv11036tS__T0001TTNATS2019012305HP001.Hdr snowdepth.nc
"""
import netCDF4
import geopandas as gpd
import cartopy.crs as ccrs
from pyiem.plot import MapPlot, nwssnow
from pyiem.util import get_dbconn

LEVELS = [0.01, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36]


def overlay_lows(mp):
    """Overlay low temperature reports."""
    pgconn = get_dbconn("iem")
    df = gpd.read_postgis(
        """
        SELECT id, geom, round(min_tmpf::numeric, 0) as low
        from summary s JOIN stations t on
        (s.iemid = t.iemid) WHERE s.day = '2020-02-20' and
        (t.network ~* 'ASOS' or t.network = 'AWOS') and
        t.country = 'US' and min_tmpf is not null ORDER by min_tmpf ASC
    """,
        pgconn,
        index_col="id",
        geom_col="geom",
    )
    mp.plot_values(
        df["geom"].x, df["geom"].y, df["low"].values, fmt="%i", labelbuffer=1
    )


def overlay(mp):
    """Overlay the alerts, please."""
    pgconn = get_dbconn("postgis")
    df = gpd.read_postgis(
        """
    SELECT u.simple_geom as geom, phenomena from warnings_2019 w JOIN ugcs u
    ON (w.gid = u.gid) WHERE phenomena in ('WW', 'BZ') and
    issue > '2019-01-23' and expire > '2019-01-24'
    """,
        pgconn,
        geom_col="geom",
    )
    print("Found %s warnings" % (len(df.index),))
    crs = ccrs.PlateCarree()
    crs_new = ccrs.PlateCarree()
    # crs_new = ccrs.Mercator()
    colors = {"BZ": "k", "WW": "k"}
    for phenomena in ["WW", "BZ"]:
        filtered_df = df[df["phenomena"] == phenomena]
        new_geometries = [
            crs_new.project_geometry(ii, src_crs=crs)
            for ii in filtered_df["geom"].values
        ]
        mp.ax.add_geometries(
            new_geometries,
            crs=crs_new,
            edgecolor="white",
            facecolor=colors[phenomena],
            alpha=0.4,
            lw=1.0,
            zorder=10,
        )
        # mp.ax.add_geometries(
        #    new_geometries, crs=crs_new,
        #    edgecolor='k', facecolor='red', alpha=.4, lw=1.5,
        #    zorder=11)


def main():
    """Go Main Go."""
    nc = netCDF4.Dataset("snowdepth.nc")
    lats = nc.variables["lat"][:]
    lons = nc.variables["lon"][:]
    snowdepth = nc.variables["Band1"][:] / 25.4  # mm to inch
    nc.close()

    mp = MapPlot(
        sector="custom",
        west=-100.1,
        east=-92,
        south=40.7,
        north=44.5,
        title=(
            r"20 Feb 2020 Morning Low Temperature ($^\circ$F) + Snow Cover"
        ),
        subtitle="12 AM 20 Feb 2020 NSIDC SNODAS Snow Depth Analysis",
    )
    cmap = nwssnow()
    cmap.set_under("white")
    mp.pcolormesh(lons, lats, snowdepth, LEVELS, cmap=cmap, units="inch")
    # overlay(mp)
    overlay_lows(mp)
    mp.postprocess(filename="200221.png")


if __name__ == "__main__":
    main()
