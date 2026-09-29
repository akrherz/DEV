"""Create a map dot plot showing planting progress."""

import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Circle
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import MapPlot
from pyiem.reference import Z_OVERLAY2
from tqdm import tqdm


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("dep") as conn:
        fieldsdf = pd.read_sql(
            sql_helper("""
            select st_x(st_transform(st_centroid(f.geom), 4326)) as lon,
           st_y(st_transform(st_centroid(f.geom), 4326)) as lat,
           till1, till2, till3, plant from field_operations o
           JOIN field f on (o.field_id = f.field_id)
           JOIN huc12 h on (f.huc12_id = h.huc12_id)
           where o.year = 2019 and h.states ~* 'IA'
        """),
            conn,
            index_col=None,
            parse_dates=["till1", "till2", "till3", "plant"],
        )

    # Colors representing sequence through tillage and finally planting
    colors = ["tan", "#ff7f00", "#ffff00", "#00fff0", "#00ff00"]
    bins = [-1, 0, 1, 2, 3, 4, 5]
    cmap = ListedColormap(colors)

    buffer = 0.2
    progress = tqdm(enumerate(pd.date_range("2019/04/11", "2019/06/14")))
    for i, dt in progress:
        progress.set_description(f"Processing {dt.strftime('%Y-%m-%d')}")
        mp = MapPlot(
            title=f"DEP Planting Progress for {dt.strftime('%Y-%m-%d')}",
            subtitle=f"Plotting {len(fieldsdf):,} Corn/Soybean fields",
            sector="custom",
            west=fieldsdf["lon"].min() - buffer,
            east=fieldsdf["lon"].max() + buffer,
            south=fieldsdf["lat"].min() - buffer,
            north=fieldsdf["lat"].max() + buffer,
            nocaption=True,
            logo="dep",
            figsize=(12, 8),
        )
        mp.scatter(
            fieldsdf["lon"].to_numpy(),
            fieldsdf["lat"].to_numpy(),
            [-0.1] * len(fieldsdf),
            bins,
            s=1,
            cmap=cmap,
            zorder=Z_OVERLAY2,
            draw_colorbar=False,
        )
        for till in range(1, 4):
            tilled = fieldsdf[fieldsdf[f"till{till}"] <= dt]
            if not tilled.empty:
                mp.scatter(
                    tilled["lon"].to_numpy(),
                    tilled["lat"].to_numpy(),
                    [till - 0.1] * len(tilled),
                    bins,
                    s=0.3,
                    cmap=cmap,
                    alpha=0.1,
                    zorder=Z_OVERLAY2,
                    draw_colorbar=False,
                )
        planted = fieldsdf[fieldsdf["plant"] <= dt]
        if not planted.empty:
            mp.scatter(
                planted["lon"].to_numpy(),
                planted["lat"].to_numpy(),
                [4] * len(planted),
                bins,
                s=0.3,
                cmap=cmap,
                zorder=Z_OVERLAY2,
                alpha=0.1,
                draw_colorbar=False,
            )
        mp.ax.legend(
            [
                Circle((0, 0), 1, color=colors[0]),
                Circle((0, 0), 1, color=colors[1]),
                Circle((0, 0), 1, color=colors[2]),
                Circle((0, 0), 1, color=colors[3]),
                Circle((0, 0), 1, color=colors[4]),
            ],
            [
                "Not tilled",
                "Tillage 1",
                "Tillage 2",
                "Tillage 3",
                "Planted",
            ],
            loc="upper right",
        ).set_zorder(Z_OVERLAY2)

        mp.postprocess(filename=f"frames/{i:04.0f}.png")
        mp.close()


if __name__ == "__main__":
    main()
