# Attempt to read and plot a postgis polygon, this would simplify things a lot
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
import math
import iemplot
from osgeo import ogr
from shapely.wkb import loads
from numpy import asarray
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import matplotlib.patheffects as PathEffects
import Image
import mx.DateTime
from iem import constants


fig = plt.figure(num=None, figsize=(10.24,7.68))
ax = plt.axes([0.01,0,0.9,1], axisbg=(0.4471,0.6235,0.8117))  
#ak_ax = plt.axes([0.01,0.0,0.25,0.25], axisbg=(0.4471,0.6235,0.8117), anchor='SW') 
#hi_ax = plt.axes([0.48,0.0,0.2,0.2], axisbg=(0.4471,0.6235,0.8117), anchor='SW') 
#pr_ax = plt.axes([0.78,0.05,0.125,0.15], axisbg=(0.4471,0.6235,0.8117), anchor='SW')
map = Basemap(projection='lcc', fix_aspect=False,
                           urcrnrlat=constants.MW_NORTH,
                           llcrnrlat=constants.MW_SOUTH,
                           urcrnrlon=constants.MW_EAST,
                           llcrnrlon=constants.MW_WEST,
                           lat_0=45.,lon_0=-92.,lat_ts=42.,
                           resolution='i', ax=ax)
map.fillcontinents(color='0.7',zorder=0)
"""
akmap = Basemap(projection='cyl', urcrnrlat=78.1, llcrnrlat=48.08, urcrnrlon=-129.0,
             llcrnrlon=-179.5, 
             resolution='l', ax=ak_ax)
akmap.fillcontinents(color='0.7',zorder=0)

himap = Basemap(projection='cyl', urcrnrlat=22.5, llcrnrlat=18.5, urcrnrlon=-154.0,
             llcrnrlon=-161.0,
             resolution='l', ax=hi_ax)
himap.fillcontinents(color='0.7',zorder=0)
"""
#prmap = Basemap(projection='cyl', urcrnrlat=18.6, llcrnrlat=17.5, urcrnrlon=-64.0,
#             llcrnrlon=-68.0,
#             resolution='l', ax=pr_ax)
#prmap.fillcontinents(color='0.7',zorder=0)

map.drawstates()
#himap.drawstates()
#akmap.drawstates()
#prmap.drawstates()
#shp_info = map.readshapefile('/mesonet/data/gis/static/shape/4326/us/states', 'st', drawbounds=True)
#shp_info = akmap.readshapefile('/mesonet/data/gis/static/shape/4326/us/states', 'st', drawbounds=True)
#shp_info = himap.readshapefile('/mesonet/data/gis/static/shape/4326/us/states', 'st', drawbounds=True)
print 'Done drawing bounds'
"""
--- select cwa.wfo, foo2.count, cwa.the_geom from cwa LEFT OUTER JOIN 
---   (SELECT wfo, count(*) from warnings_2011 WHERE gtype = 'P'
---   and phenomena = 'TO' and significance = 'W' GROUP by wfo) as foo ON (cwa.wfo = foo.wfo)
---   ORDER by foo.count DESC NULLS LAST
--- (select wfo, count(*), round(avg(count)::numeric,2) from (select phenomena, significance, eventid, wfo, extract(year from issue) as yr, count(*) from warnings where issue > '2007-10-01' and phenomena = 'TO' and significance = 'W' and gtype = 'C' GROUP by yr, phenomena, significance, eventid, wfo) as foo GROUP by wfo) 

"""

source = ogr.Open("PG:host=127.0.0.1 dbname=postgis user=akrherz")
data = source.ExecuteSQL("""
 select cwa.wfo,   foo2.data as mydata, ST_SnapToGrid(cwa.the_geom,0.001), x(ST_Centroid(cwa.the_geom)),
 y(ST_Centroid(cwa.the_geom)) from cwa LEFT OUTER JOIN
--- (SELECT wfo, avg(ST_Area(ST_Transform(geom,2163))) / 1000000. as data from warnings WHERE phenomena in ('SV','TO') and
--- significance = 'W' and gtype = 'P' and issue > '2007-10-01' GROUP by wfo)

--- (SELECT wfo, sum(case when tml_direction > 180 and tml_direction < 360 then 1 else 0 end) / count(*)::numeric * 100
--- as data from sbw WHERE issue > '2007-10-01' and status = 'NEW' and phenomena in ('SV','TO')
--- GROUP by wfo)

--- (SELECT wfo, avg(tml_sknt) * 1.15 as data from sbw WHERE 
--- issue > '2007-10-01' and status = 'NEW' and
--- phenomena = 'SV' and tml_sknt >= 0 and extract(month from issue) = 5
--- GROUP by wfo)

--(select wfo, data1 / data3 as data from (SELECT wfo, sum(case when tml_geom is not null then 1 else 0 end)::numeric as data1,  sum(case when tml_geom_line is not null then 1 else 0 end)::numeric as data3
-- from sbw where issue > '2007-10-01' and status = 'NEW' and
-- phenomena = 'SV' and (tml_geom is not null or tml_geom_line is not null) 
-- GROUP by wfo) as foooo WHERE data3 > 0)

 (select wfo, col3  as data from ferree3)

--- (select wfo, sum(case when (overlap / perimeter) >= 0.9 then 1 else 0 end) / count(*)::numeric * 100.0 as data from ferree GROUP by wfo)

--- (select wfo, sum(case when (init_expire - issue) > '60 minutes'::interval then 1 else 0 end) / count(*)::numeric * 100.0 as data
--- from sbw where phenomena = 'TO' and significance = 'W' and status = 'NEW' 
--- and issue > '2010-10-01' group by wfo)

--- (SELECT wfo, count(*) as data from sbw_2012 WHERE phenomena in ('TO') and 
--- status = 'NEW' and issue < '2012-05-15' GROUP by wfo)

-- (select wfo, sum(case when count = 1 then 1 else 0 end) / count(*)::numeric * 100.0 as data
--- from (select wfo, eventid, phenomena, count(*) from sbw 
--- where phenomena in ('TO','SV') and significance = 'W' and issue > '2010-10-01' 
--- GROUP by eventid, phenomena, wfo) as foo3 GROUP by wfo)

-- (select wfo, ts, count as data from (select wfo, ts, count, row_number() over (partition by wfo ORDER by count DESC, ts DESC) as rn from (select wfo, ts, count(*) from (select eventid, wfo, generate_series(issue, expire - '1 minute'::interval, '1 minute'::interval) as ts from warnings_2011 where gtype = 'P' and phenomena in ('SV','TO') and significance = 'W') as foo GROUP by wfo, ts ORDER by count DESC) as foo22 ORDER by count DESC) as foo3 WHERE rn = 1 ORDER by count DESC)

--- (select case when wfo = 'JSJ' then 'SJU' else wfo end as wfo, avg(data) as data from (select wfo, extract(year from d) as yr, 
--- count(*) as data from (select distinct wfo,  
--- date((issue at time zone 'UTC')+'15 hours'::interval) as d from warnings 
--- where gtype = 'P' and significance = 'W' and phenomena in ('TO') and issue > '2005-01-01') as foo 
--- GROUP by wfo, yr) as foo3 GROUP by wfo)

--- (select case when wfo = 'JSJ' then 'SJU' else wfo end as wfo, count(*) / 10 as data from sbw where
--- significance = 'W' and phenomena in ('TO') and issue > '2002-01-01'
--- and issue < '2012-01-01'  and status = 'NEW'  GROUP by wfo)



as foo2 ON (cwa.wfo = foo2.wfo)
ORDER by mydata DESC NULLS LAST
""")

LBLFMT='%.0f'
print 'Here'
maxV = None
#maxV = 25000
patches = []
lats = []; lons = []; labels = []
akpatches = []
aklats = []; aklons = []; aklabels = []
hipatches = []
hilats = []; hilons = []; hilabels = []
prpatches = []
prlats = []; prlons = []; prlabels = []
while 1:
    feature = data.GetNextFeature()
    #print dir(feature)
    if not feature:
        break
    if feature.GetField('wfo') in ['',None]:
        continue
    cnt = feature.GetField('mydata')
    ts = None
    #if feature.GetField('ts') is not None:
    #  ts = mx.DateTime.strptime(feature.GetField('ts')[:10], '%Y/%m/%d')
    if not maxV:
        maxV = cnt + 0.01
    if cnt is None or cnt == 0:
        c = 'w'
        cnt = 0
    else:
        c = iemplot.floatRgb(cnt,0,maxV)
        c = rgb2hex(c)
    geom = loads(feature.GetGeometryRef().ExportToWkb())
    print feature.GetField('wfo'), feature.GetField('mydata')
    for polygon in geom:
        a = asarray(polygon.exterior)
        if feature.GetField('wfo') in ['AFC', 'AFG', 'AJK']:
            continue
            x,y = akmap(a[:,0], a[:,1])
            a2 = zip(x,y)
            p = Polygon(a2,fc=c,ec='k',zorder=2, lw=.1)
            akpatches.append(p)
            #if ts is not None:
            aklats.append( float(feature.GetField('y')) )
            aklons.append( float(feature.GetField('x')) )
            aklabels.append( LBLFMT % (cnt,) )
        elif feature.GetField('wfo') in ['HFO', 'PPG']:
            continue
            x,y = himap(a[:,0], a[:,1])
            a2 = zip(x,y)
            p = Polygon(a2,fc=c,ec='k',zorder=2, lw=.1)
            hipatches.append(p)
            #if ts is not None:
            hilats.append( float(feature.GetField('y')) )
            hilons.append( float(feature.GetField('x')) )
            hilabels.append( LBLFMT %(cnt,) )
        elif feature.GetField('wfo') in ['JSJ2','SJU2']:
            continue
            x,y = prmap(a[:,0], a[:,1])
            a2 = zip(x,y)
            p = Polygon(a2,fc=c,ec='k',zorder=2, lw=.1)
            prpatches.append(p)
            #if ts is not None:
            prlats.append( float(feature.GetField('y')) )
            prlons.append( float(feature.GetField('x')) )
            prlabels.append( LBLFMT %(cnt,) )
        else:
            x,y = map(a[:,0], a[:,1])
            a2 = zip(x,y)
            p = Polygon(a2,fc=c,ec='k',zorder=2, lw=.1)
            patches.append(p)
            #if ts is not None:
            lats.append( float(feature.GetField('y')) )
            lons.append( float(feature.GetField('x')) )
            labels.append( LBLFMT % (cnt,) )
        
        

ax.add_collection( PatchCollection(patches,match_original=True) )
#ak_ax.add_collection( PatchCollection(akpatches,match_original=True) )
#hi_ax.add_collection( PatchCollection(hipatches,match_original=True) )
#pr_ax.add_collection( PatchCollection(prpatches,match_original=True) )
print 'MAXV is', maxV
iemplot.bmap_clrbar(maxV,label='percent',levels=16)

xs,ys = map(lons, lats)
for i in range(len(xs)):
    txt = ax.text(xs[i], ys[i], '%s' % (labels[i],), verticalalignment='center', horizontalalignment='center', size='small')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])

"""
xs,ys = akmap(aklons, aklats)
for i in range(len(xs)):
    txt = ak_ax.text(xs[i], ys[i], '%s' % (aklabels[i],), verticalalignment='center', horizontalalignment='center', size='small')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="w")])
xs,ys = himap(hilons, hilats)
for i in range(len(xs)):
    txt = hi_ax.text(xs[i], ys[i], '%s' % (hilabels[i],), verticalalignment='center', horizontalalignment='center', size='small')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="w")])
"""
#xs,ys = himap(prlons, prlats)
#for i in range(len(xs)):
#  pr_ax.text(xs[i], ys[i], "%s" % (prlabels[i],), verticalalignment='center', horizontalalignment='center', size='small')

#for nshape,seg in enumerate(map.st):
#    poly=Polygon(seg,fc='',ec='k',zorder=2, lw=.1)
#    ax.add_patch(poly)

# Top label
# bbox=dict(boxstyle='square', facecolor='w', ec='b'),
ax.text(0.17, 1.1, "2012 Percent of Average Severe Thunderstorm + Tornado Warnings Jan 1 - May 15", transform=ax.transAxes,
     size=12,
    horizontalalignment='left', verticalalignment='center')
#ax.text(0.17, 1.05, "Excluded VTEC codes: BH,CF,FA,FF,FL,GL,LO,LS,MA,MF,MS,MH,RB,RP,SC,SE,SI,SU,SV,SW,TO", transform=ax.transAxes,
#ax.text(0.17, 1.05, "Excluded VTEC codes: CF,FA,FF,FL,LS,SV,TO", transform=ax.transAxes,
#ax.text(0.17, 1.05, "Only VTEC codes: Fog FG, Flood FL, Wind WI and Only Significance: Advisory Y", transform=ax.transAxes,
#     size=12,
#    horizontalalignment='left', verticalalignment='center')

#ax.text(0.17, 1.005, 'Map Generated: %s, Period: 1 Jan 2009 - 31 Dec 2012' % (mx.DateTime.now().strftime("%d %B %Y %I:%M %p %Z"),), transform=ax.transAxes,
#     size=9,
#    horizontalalignment='left', verticalalignment='bottom')

# Logo!
logo = Image.open('../../htdocs/images/logo_small.png')
ax3 = plt.axes([0.05,0.87,0.1,0.1], frameon=False, axisbg=(0.4471,0.6235,0.8117), yticks=[], xticks=[])
ax3.imshow(logo)

#plt.text(0.08, 0.035,'Iowa State University', size='small', color='#222d7d',
#     horizontalalignment='center',
#     verticalalignment='center',
#     transform = ax.transAxes)



fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')
