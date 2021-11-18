import matplotlib.pyplot as plt
import matplotlib.cm as mpcm
import matplotlib.colors as mpcolors

cmap = plt.get_cmap("viridis")
clevs = list(range(-94, -85))
norm = mpcolors.BoundaryNorm(clevs, cmap.N)
plt.colorbar(
    mpcm.ScalarMappable(cmap=cmap, norm=norm),
)
