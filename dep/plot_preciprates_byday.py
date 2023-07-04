"""Generate a visual showing rainfall rates."""
import calendar

import numpy as np

from matplotlib import rcParams
from metpy.units import units
from pyiem.dep import read_cli
from pyiem.plot import figure_axes

rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Liberation Sans"],
    }
)


def main():
    """Go Main Go."""
    df = read_cli("/i/0/cli/093x041/093.61x041.98.cli")
    df["jday"] = df.index.strftime("%j").astype("i")
    df["maxr"] = (df["maxr"].values * units("mm")).to(units("inch")).m

    (fig, ax) = figure_axes(
        logo="dep",
        figsize=(8, 6),
        title=(
            "DEP 2007-2023 Maximum Precipitation Rate\n"
            "For Ames, Iowa (41.98N 93.61W)"
        ),
    )
    print(df[df["jday"] > 330].sort_values("maxr", ascending=False))
    gdf = df[["jday", "maxr"]].groupby("jday").max()
    sgdf = gdf.rolling(28, center=True, min_periods=1).mean()
    """
    ax.plot(
        gdf.index - 14,
        gdf["maxr"],
        color="k",
        lw=2,
        ls=":",
        label=r"Shifted -14$d$",
    )
    """
    ax.scatter(
        gdf.index,
        gdf["maxr"],
        color="tan",
        label="Daily Max",
    )
    ax.plot(
        sgdf.index,
        sgdf["maxr"],
        color="k",
        lw=2,
        label="28$d$ averaged",
    )
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.legend()
    ax.set_ylabel(r"Precipitation Rate inch $h^{-1}$")
    ax.grid(True, color="k")
    # ax.set_xlim(60, 213)
    ax.set_yticks(np.arange(0, 6.1, 0.5))
    ax.set_ylim(-0.2, 6.01)
    ax.set_xlim(-2, 367)
    ax.set_xlabel("Day of Year")
    fig.savefig("230703.png")


if __name__ == "__main__":
    main()
