"""Generate a visual showing rainfall rates."""
import calendar

from matplotlib import rcParams

rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Liberation Sans"],
    }
)

from pyiem.dep import read_cli
from pyiem.plot import figure_axes
from pyiem.plot.use_agg import plt
from metpy.units import units


def main():
    """Go Main Go."""
    df = read_cli("/i/0/cli/093x041/093.61x041.98.cli")
    df["jday"] = df.index.strftime("%j").astype("i")
    df["maxr"] = (df["maxr"].values * units("mm")).to(units("mm")).m
    gdf = df[["jday", "maxr"]].groupby("jday").max()

    (fig, ax) = figure_axes(
        logo="dep",
        figsize=(8, 6),
        title=(
            "DEP 2007-2020 Maximum Precipitation Rate\n"
            "For Ames, Iowa (41.98N 93.61W), March thru July"
        ),
    )
    gdf = (
        df[["jday", "maxr"]]
        .groupby("jday")
        .max()
        .rolling(28, center=True)
        .mean()
    )
    ax.plot(
        gdf.index - 14,
        gdf["maxr"],
        color="k",
        lw=2,
        ls=":",
        label=r"Shifted -14$d$",
    )
    ax.plot(
        gdf.index,
        gdf["maxr"],
        color="k",
        lw=2,
        label="Observed 28$d$ averaged",
    )
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax.set_xticklabels(calendar.month_name[1:])
    ax.legend()
    ax.set_ylabel(r"Precipitation Rate $mm$ $h^{-1}$")
    ax.grid(True, color="k")
    ax.set_xlim(60, 213)
    ax.set_yticks(range(0, 101, 25))
    ax.set_xlabel("Month")
    fig.savefig("test.png", dpi=300)


if __name__ == "__main__":
    main()
