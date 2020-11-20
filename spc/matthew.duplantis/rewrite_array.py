import numpy as np

lats = []
lons = []
for line in open("config/us_shapefile_points.txt"):
    tokens = line.split(",")
    lats.append(float(tokens[1].strip()))
    lons.append(float(tokens[0]))

lats.append(lats[0])
lons.append(lons[0])

lats = np.array(lats)
lons = np.array(lons)

"""
f = open('conus.numpy', 'wb')
np.save(f, lons)
np.save(f, lats)
f.close()

f = open('conus.numpy', 'rb')
lons = np.load(f)
lats = np.load(f)
f.close()

"""
