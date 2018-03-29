"""Make a plot of all the bot warnings"""

import cartopy.crs as ccrs
from geopandas import read_postgis
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main"""
    pgconn = get_dbconn('postgis')
    df = read_postgis("""
    select geom, issue from sbw where wfo = 'LBF' and phenomena = 'TO'
    and significance = 'W' and status = 'NEW' and issue > '2007-10-01'
    and issue < '2018-01-01'
    """, pgconn, geom_col='geom', crs={'init': 'epsg:4326', 'no_defs': True})

    bounds = df['geom'].total_bounds
    # bounds = [-102.90293903,   40.08745967,  -97.75622311,   43.35172981]
    bbuf = 0.25
    mp = MapPlot(sector='custom', west=bounds[0] - bbuf,
                 south=bounds[1] - bbuf,
                 east=bounds[2] + bbuf, north=bounds[3] + bbuf,
                 continentalcolor='white',
                 title='NWS North Platte Issued Tornado Warnings [2008-2017]',
                 subtitle='%s warnings plotted' % (len(df.index), ))
    crs_new = ccrs.Mercator()
    crs = ccrs.PlateCarree()
    new_geometries = [crs_new.project_geometry(ii, src_crs=crs)
                      for ii in df['geom'].values]
    # mp.draw_cwas()
    mp.ax.add_geometries(new_geometries, crs=crs_new, lw=0.5,
                         edgecolor='red', facecolor='None', alpha=1,
                         zorder=5)
    # mp.drawcounties()
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
