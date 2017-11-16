"""Make a spatial histogram of SBWs"""
from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn('postgis', user='nobody')
    df = read_sql("""
    WITH wlocs as (
        SELECT id, st_x(st_transform(geom, 2163)) as x,
        ST_y(st_transform(geom, 2163)) as y from stations
        where network = 'WFO'),
    centroids as (
        SELECT wfo, st_centroid(st_transform(geom, 2163)) as geo
        from sbw WHERE issue > '2008-01-01' and status = 'NEW'
        and phenomena = 'FF' and significance = 'W')

    SELECT ST_x(c.geo) - w.x as x, ST_y(c.geo) - w.y as y
    from centroids c JOIN wlocs w ON (c.wfo = w.id) 
    
    """, pgconn, index_col=None)
    axis = np.arange(-300, 301, 10)
    h2d, xedges, yedges = np.histogram2d(df['x'] / 1000., df['y'] / 1000.,
                                         axis)
    h2d = np.ma.array(h2d)
    h2d.mask = np.ma.where(h2d < 1, True, False)
    maxval = np.nanmax(h2d)
    (fig, ax) = plt.subplots(1, 1)
    ax.set_xlabel("X Distance from WFO [km]")
    ax.set_ylabel("Y Distance from WFO [km]")
    ax.set_title(("2008-2017 Frequency of Storm Based Flash Flood Warning\n"
                  "distance from polygon centroid to issuing WFO location"))
    fig.text(0.02, 0.01, "@akrherz 16 Nov 2017")
    fig.text(0.99, 0.01, "computed in US Albers EPSG:2163", ha='right')
    res = ax.pcolormesh(xedges, yedges, h2d.transpose() / maxval)
    for rng in range(25, 201, 25):
        circle = plt.Circle((0, 0), rng, edgecolor='r', facecolor='None')
        ax.add_artist(circle)
    ax.grid(True)
    fig.colorbar(res, label='Normalized Count (max: %.0f)' % (maxval, ))
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
