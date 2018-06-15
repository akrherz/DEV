"""MRMS Plotting util for zoomed in areas"""
from __future__ import print_function
import pygrib
import shapefile
from pandas.io.sql import read_sql
from shapely.geometry import shape
import cartopy.crs as ccrs
from pyiem.plot import MapPlot, nwsprecip, Z_OVERLAY2
from pyiem.datatypes import distance
from pyiem.util import get_dbconn


def get_data():
    """Get data"""
    lons = []
    lats = []
    vals = []
    labels = []
    pgconn = get_dbconn('postgis')
    df = read_sql("""
    SELECT st_x(geom) as lon, st_y(geom) as lat, magnitude from lsrs_2018
    where wfo = 'DMX' and valid between '2018-06-14 10:00' and '2018-06-18'
    and typetext = 'HEAVY RAIN' ORDER by magnitude DESC
    """, pgconn, index_col=None)
    print(df)
    return df.lon.values, df.lat.values, df.magnitude.values, None
    cursor = pgconn.cursor()
    for network in ['IA_ASOS', 'AWOS', 'IA_COOP', 'IACOCORAHS']:
        cursor.execute("""
        SELECT id, st_x(geom), st_y(geom), sum(pday)
        from summary_2017 s JOIN stations t
        on (s.iemid = t.iemid) WHERE s.day in ('2017-09-20', '2017-09-21')
        and t.network = %s
        and pday > 0 GROUP by id, st_x, st_y
        ORDER by sum DESC
        """, (network, ))
        for row in cursor:
            lons.append(row[1])
            lats.append(row[2])
            vals.append("%.2f" % (row[3], ))
            labels.append(row[0])
    return lons, lats, vals, labels


def main():
    """Go!"""
    title = 'NOAA MRMS Q3: RADAR + Guage Corrected Rainfall Estimates + NWS Storm Reports'
    mp = MapPlot(sector='custom',
                 north=42.3, east=-93.0, south=41.65, west=-94.1,
                 axisbg='white',
                 titlefontsize=14,
                 title=title,
                 subtitle='Valid: 14 June 2018')

    shp = shapefile.Reader('cities.shp')
    for record in shp.shapeRecords():
        geo = shape(record.shape)
        mp.ax.add_geometries([geo], ccrs.PlateCarree(), zorder=Z_OVERLAY2,
                             facecolor='None', edgecolor='k', lw=2)

    grbs = pygrib.open('MRMS_GaugeCorr_QPE_24H_00.00_20180614-200000.grib2')
    grb = grbs.message(1)
    pcpn = distance(grb['values'], 'MM').value('IN')
    lats, lons = grb.latlons()
    lons -= 360.
    clevs = [0.01, 0.1, 0.3, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
    cmap = nwsprecip()
    cmap.set_over('k')

    mp.pcolormesh(lons, lats, pcpn, clevs, cmap=cmap, latlon=True,
                  units='inch')
    lons, lats, vals, labels = get_data()
    mp.drawcounties()
    mp.plot_values(lons, lats, vals, "%s", labels=labels,
                   labelbuffer=1, labelcolor='white')

    mp.drawcities(labelbuffer=5, minarea=0.2)
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
