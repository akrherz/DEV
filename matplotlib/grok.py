import matplotlib.colors as mpcolors
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.mpl as mpl
import numpy

cpool = [
    "#e6e6e6",
    "#d2d2d2",
    "#bcbcbc",
    "#969696",
    "#646464",
    "#1464d2",
    "#1e6eeb",
    "#2882f0",
    "#3c96f5",
    "#50a5f5",
    "#78b9fa",
    "#96d2fa",
    "#b4f0fa",
    "#e1ffff",
    "#0fa00f",
    "#1eb41e",
    "#37d23c",
    "#50f050",
    "#78f573",
    "#96f58c",
    "#b4faaa",
    "#c8ffbe",
    "#ffe878",
    "#ffc03c",
    "#ffa000",
    "#ff6000",
    "#ff3200",
    "#e11400",
    "#c00000",
    "#a50000",
    "#643c32",
    "#785046",
    "#8c645a",
    "#b48c82",
    "#e1beb4",
    "#f0dcd2",
    "#ffc8c8",
    "#f5a0a0",
    "#f5a0a0",
    "#e16464",
    "#c83c3c",
]

cmap3 = mpcolors.ListedColormap(cpool, "fancycolors")
cmap3.set_over("#000000")
cmap3.set_under("#FFFFFF")
cmap3.set_bad("#FFFFFF")
cm.register_cmap(cmap=cmap3)

levels = [
    0.0,
    0.01,
    0.1,
    0.25,
    0.5,
    0.75,
    1,
    1.25,
    1.5,
    2,
    2.5,
    3,
    4,
    5,
    7,
    10,
    20,
    30,
    40,
    50,
]

data = numpy.reshape(levels * len(levels), (len(levels), len(levels)))
# modify for a test
data[10, :] = data[10, :] + 10.0
data[11, :] = data[11, :] - 10.0
norm = mpcolors.BoundaryNorm(levels, len(cpool))

fig = plt.figure(num=None, figsize=(8, 8))
fig.subplots_adjust(bottom=0, left=0, right=1, top=1, wspace=0, hspace=0)
ax = plt.axes([0.1, 0.05, 0.8, 0.85], axisbg=(0.4471, 0.6235, 0.8117))

cs = ax.imshow(
    data, aspect="auto", cmap=cmap3, interpolation="nearest", norm=norm
)

ax3 = plt.axes([0.92, 0.1, 0.02, 0.8], frameon=False, yticks=[], xticks=[])

cb2 = mpl.colorbar.ColorbarBase(
    ax3,
    cmap=cmap3,
    norm=norm,
    boundaries=[-1] + levels + [51],
    extend="both",
    format="%g",
    ticks=levels,  # optional
    spacing="uniform",
    orientation="vertical",
)
cb2.ax.set_xlabel("units")

fig.savefig("test.png")
