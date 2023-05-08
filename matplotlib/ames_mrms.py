"""MRMS Plotting util for zoomed in areas"""
import pygrib
import shapefile

import cartopy.crs as ccrs
from pyiem.plot import Z_OVERLAY2, MapPlot, nwsprecip
from pyiem.util import get_dbconn, mm2inch
from shapely.geometry import shape


def get_data():
    """Get data"""
    lons = []
    lats = []
    vals = []
    labels = []
    pgconn = get_dbconn("iem")

    cursor = pgconn.cursor()
    networks = ["IA_ASOS", "AWOS", "OT", "IA_DCP"]
    cursor.execute(
        """
    SELECT id, st_x(geom), st_y(geom), sum(pday)
    from summary_2021 s JOIN stations t
    on (s.iemid = t.iemid) WHERE s.day = '2021-06-09'
    and t.network in %s
    and pday > 0 GROUP by id, st_x, st_y
    ORDER by sum DESC
    """,
        (tuple(networks),),
    )
    for row in cursor:
        lons.append(row[1])
        lats.append(row[2])
        vals.append("%.2f" % (row[3],))
        labels.append(row[0])
    return lons, lats, vals, labels


def main():
    """Go!"""
    title = "NOAA MRMS Q3: RADAR + Guage Corrected Rainfall Estimates"
    mp = MapPlot(
        sector="custom",
        north=42.1,
        east=-93.55,
        south=41.95,
        west=-93.7,
        axisbg="white",
        titlefontsize=14,
        title=title,
        subtitle="Valid: 9 June 2021",
    )

    shp = shapefile.Reader("cities.shp")
    for record in shp.shapeRecords():
        geo = shape(record.shape)
        mp.ax.add_geometries(
            [geo],
            ccrs.PlateCarree(),
            zorder=Z_OVERLAY2,
            facecolor="None",
            edgecolor="brown",
            lw=2,
        )

    shp = shapefile.Reader("high.shp")
    for record in shp.shapeRecords():
        geo = shape(record.shape)
        mp.ax.add_geometries(
            [geo],
            ccrs.PlateCarree(),
            zorder=Z_OVERLAY2,
            edgecolor="k",
            facecolor="None",
            lw=2,
        )

    grbs = pygrib.open("RadarOnly_QPE_24H_00.00_20210610-010000.grib2")
    grb = grbs.message(1)
    pcpn = mm2inch(grb["values"])
    lats, lons = grb.latlons()
    lons -= 360.0
    clevs = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    cmap = nwsprecip()
    cmap.set_over("k")

    mp.pcolormesh(
        lons,
        lats,
        pcpn,
        clevs,
        cmap=cmap,
        latlon=True,
        units="inch",
        spacing="proportional",
    )
    mp.drawcounties()
    """
    lons, lats, vals, labels = get_data()
    mp.plot_values(
        lons,
        lats,
        vals,
        "%s",
        labels=labels,
        labelbuffer=1,
        labelcolor="white",
    )
    """
    mp.drawcities(labelbuffer=5, minarea=0.2)
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
