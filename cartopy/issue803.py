import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

fig = plt.figure()

ax = fig.add_subplot(111, projection=ccrs.LambertConformal())
feature = cartopy.feature.NaturalEarthFeature(name='coastline', category='physical',
                                              scale='110m',
                                              edgecolor='#000000', facecolor='#AAAAAA')
ax.add_feature(feature)
plt.show()
