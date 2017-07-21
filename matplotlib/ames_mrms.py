"""MRMS Plotting util for zoomed in areas"""

import pygrib
from pyiem.plot import MapPlot, nwsprecip, Z_OVERLAY2
from pyiem.datatypes import distance
import shapefile
from shapely.geometry import shape
import cartopy.crs as ccrs


def main():
    """Go!"""
    title = 'NOAA MRMS Q3: RADAR+Gauge Corr Estimated Precipitation'
    mp = MapPlot(sector='custom',
                 north=42.3, east=-93.0, south=41.45, west=-94.1,
                 axisbg='white',
                 title=title,
                 subtitle='Valid: 8 AM 20 July - 8 AM 21 July 2017')

    shp = shapefile.Reader('cities.shp')
    for record in shp.shapeRecords():
        geo = shape(record.shape)
        mp.ax.add_geometries([geo], ccrs.PlateCarree(), zorder=Z_OVERLAY2,
                             facecolor='None', edgecolor='k', lw=2)

    grbs = pygrib.open('MRMS_GaugeCorr_QPE_24H_00.00_20170721-130000.grib2')
    grb = grbs.message(1)
    pcpn = distance(grb['values'], 'MM').value('IN')
    lats, lons = grb.latlons()
    lons -= 360.
    clevs = [0.01, 0.1, 0.3, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
    cmap = nwsprecip()
    cmap.set_over('k')

    mp.pcolormesh(lons, lats, pcpn, clevs, cmap=cmap, latlon=True,
                  units='inch')

    mp.drawcities(labelbuffer=5, minarea=0.2)
    mp.drawcounties()
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
