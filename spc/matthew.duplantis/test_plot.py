import numpy as np
from pyiem.plot import MapPlot

lats = []
lons = []
for line in open("config/us_shapefile_points.txt"):
    tokens = line.split(",")
    lats.append(float(tokens[1].strip()))
    lons.append(float(tokens[0]))

lats.append(lats[0])
lons.append(lons[0])

mlats = []
mlons = []
for line in open("config/us_shapefile_points_with_marine.txt"):
    tokens = line.split(",")
    mlats.append(float(tokens[1].strip()))
    mlons.append(float(tokens[0]))
mlats = np.array(mlats)
mlons = np.array(mlons)

m = MapPlot(sector="conus")

xi, yi = m.map(lons, lats)
m.ax.plot(xi, yi, lw=3, c="r")

xi, yi = m.map(mlons, mlats)
m.ax.plot(xi, yi, lw=3, c="g")

m.postprocess(view=True)
