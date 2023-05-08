import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

fig = plt.figure()

ax = fig.add_subplot(111, projection=ccrs.Mercator())
feature = cfeature.NaturalEarthFeature(
    name="ocean",
    category="physical",
    scale="10m",
    edgecolor="#000000",
    facecolor="#AAAAAA",
)
ax.add_feature(feature)
fig.savefig("test.png")
