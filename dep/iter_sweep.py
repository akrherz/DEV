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

    yaxis = np.arange(0, 30)

    # Soil Water
    soil_water = 0.02
    lines[183] = f"{soil_water:.2f}\n"
    lines[189] = f"{soil_water:.2f} " * 12 + "\n"
    lines[190] = f"{soil_water:.2f} " * 12 + "\n"
    # GMD
    gmd = 0.52
    lines[145] = f"{gmd:.2f}\n"
    # Roughness
    roughness = 25.0
    lines[211] = f" 10 {roughness:.2f} 0\n"
    # Biomass
    biomass = 0.0
    lines[113] = f"{biomass:.2f}\n"
    # Crop height
    crop_height = 0.0
    lines[85] = f"{crop_height:.2f}\n"
    lines[88] = f"{crop_height:.2f}\n"
    # Sand content
    sand = 0.04
    lines[129] = f"{sand:.2f}\n"
    lines[133] = f"{(0.79 - sand):.2f}\n"

    xaxis = np.arange(0.0, 1.0, 0.05)
    erosion = np.zeros((len(yaxis), len(xaxis)))

    for i, crop_height in tqdm(enumerate(xaxis), total=len(xaxis)):
        lines[85] = f"{crop_height:.2f}\n"
        lines[88] = f"{crop_height:.2f}\n"
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
        title="SWEPP Sensitivity Wind Speed vs Crop Height",
        subtitle=(
            r"Erosion kg m$^{-2}$, "
            f"GMD={gmd:.2f}mm, Roughness={roughness:.0f}mm, "
            f"Sand={sand:.2f} Mg/Mg, "
            f"Soil Water={soil_water:.2f} Mg/Mg, "
            f"Residue Cover={biomass:.2f} m2/m2, "
            f"Crop Height=Varies"
        ),
    )
    cmap = get_cmap("viridis")
    maxval = max(0.04, np.max(erosion))
    levels = np.arange(0, maxval, 0.02)
    levels[0] = 0.001
    cmap.set_under("white")
    norm = BoundaryNorm(levels, cmap.N)

    print("Mean grid value: {:.4f}".format(np.mean(erosion)))
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
    ax.set_xlabel("Crop Height (m)")
    ax.set_ylabel("Hourly Wind Speed (m/s)")
    fig.savefig("erosion.png")


if __name__ == "__main__":
    main()
