from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import datetime

m = Basemap()

print datetime.datetime.now()
m.readshapefile(
    "/mesonet/data/gis/static/shape/4326/nws/0.01/states",
    "states",
    drawbounds=False,
)
print datetime.datetime.now()

for nshape, seg in enumerate(m.states):
    pass
print datetime.datetime.now()
