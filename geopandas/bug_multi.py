"""Exercise bugs."""

from shapely.geometry import Polygon, GeometryCollection
import geopandas as gpd

poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
gc = GeometryCollection([poly, poly])
df = gpd.GeoDataFrame({"geometry": [poly, gc]})
df["fc"] = "white"
df.plot(fc=df["fc"])
