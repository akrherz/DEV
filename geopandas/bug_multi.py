"""Exercise bugs."""

import geopandas as gpd
from shapely.geometry import GeometryCollection, Polygon

poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
gc = GeometryCollection([poly, poly])
df = gpd.GeoDataFrame({"geometry": [poly, gc]})
df["fc"] = "white"
df.plot(fc=df["fc"])
