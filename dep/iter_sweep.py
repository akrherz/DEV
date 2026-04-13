import subprocess

import numpy as np
from matplotlib.colors import BoundaryNorm
from pyiem.plot import figure_axes, get_cmap
from tqdm import tqdm


def main():
    """Go Main Go."""
    fn = "/i/0/sweepin/07040008/0803/070400080803_90.sweepin"
    with open(fn) as fh:
        lines = fh.readlines()

    xaxis = np.arange(0.0, 0.21, 0.01)
    yaxis = np.arange(0, 30)

    erosion = np.zeros((len(yaxis), len(xaxis)))

    # Soil Water
    xval = 0.02
    lines[183] = f"{xval:.2f}\n"
    lines[189] = f"{xval:.2f} " * 12 + "\n"
    lines[190] = f"{xval:.2f} " * 12 + "\n"
    # GMD
    xval = 1.0
    lines[145] = f"{xval:.2f}\n"
    # Roughness
    xval = 25.0
    lines[211] = f" 10 {xval:.2f} 0\n"
    # Biomass
    xval = 0.2
    lines[113] = f"{xval:.2f}\n"
    # Crop height
    xval = 0.0
    lines[85] = f"{xval:.2f}\n"
    lines[88] = f"{xval:.2f}\n"

    for i, xval in tqdm(enumerate(xaxis), total=len(xaxis)):
        lines[129] = f"{xval:.2f}\n"
        lines[133] = f"{(0.77 - xval):.2f}\n"
        for j, yval in enumerate(yaxis):
            for linenum in range(220, 224):
                lines[linenum] = f"{yval:.1f} " * 6 + "\n"
            with open(fn, "w") as fh:
                fh.writelines(lines)
            subprocess.run(
                ["/opt/dep/bin/sweep", f"-i{fn}", "-Erod"],
                check=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )
            with open("/i/0/sweepin/07040008/0803/070400080803_90.erod") as fh:
                erosion[j, i] = float(fh.readlines()[0].split()[0])

    (fig, ax) = figure_axes(
        title="SWEPP Sensitivity Wind Speed vs Sand Content (minus Silt)",
        subtitle=(
            "Erosion kg m$^{-2}$, GMD=1mm, Roughness=25mm, "
            "Soil Water=0.02 Mg/Mg, Biomass=0.2 m2/m2, Crop Height=0"
        ),
    )
    cmap = get_cmap("viridis")
    maxval = max(0.04, np.max(erosion))
    levels = np.arange(0, maxval, 0.02)
    levels[0] = 0.001
    cmap.set_under("white")
    norm = BoundaryNorm(levels, cmap.N)

    res = ax.imshow(
        erosion,
        origin="lower",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
        aspect="auto",
        extent=(xaxis[0], xaxis[-1], yaxis[0], yaxis[-1]),
    )
    cax = fig.add_axes((0.92, 0.1, 0.02, 0.8))
    fig.colorbar(res, cax=cax, extend="both", label="Erosion kg m$^{-2}$")
    ax.set_xlabel("Sand Content (m3/m3)")
    ax.set_ylabel("Hourly Wind Speed (m/s)")
    fig.savefig("erosion.png")


if __name__ == "__main__":
    main()
