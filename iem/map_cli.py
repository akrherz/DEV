"""Map cli_data"""

import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot


def main():
    """Map some CLI data"""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
        WITH data as (
            select station, count(*),
            sum(case when cardinality(high_record_years) > 1 then 1 else 0 end)
            ::float / count(*)::float * 100. as freq from cli_data
            where valid > '2025-10-12' and
            cardinality(high_record_years) >= 1 group by station)

        select station, st_x(geom) as lon, st_y(geom) as lat, c.freq as val
        from data c JOIN stations s on ('K'||s.id = c.station)
        WHERE s.network ~* 'ASOS' and archive_begin < '1980-01-01'
        and c.count > 320
        order by c.freq DESC
        """,
            conn,
            index_col=None,
        )

    hex_colors = ["#FFFFFF", "#FFD200", "#FF5500", "#E6005C"]
    cmap = LinearSegmentedColormap.from_list("text_ramp", hex_colors)
    clevs = list(range(0, 41, 10))
    norm = Normalize(vmin=0, vmax=40)
    df["color"] = df["val"].apply(lambda x: cmap(norm(x)))

    mp = MapPlot(
        sector="conus",
        axisbg="tan",
        title="Frequency of Daily Record High Occurring in Multiple Years",
        subtitle="Based on NWS CLI reporting sites having at least 50 years",
    )
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["val"].values,
        outlinecolor="#111111",
        textoutlinewidth=3.5,
        fmt="%.0f",
        textsize=11,
        color=df["color"].values,
        labelbuffer=1,
    )
    mp.draw_colorbar(
        clevs,
        norm=norm,
        cmap=cmap,
        extend="neither",
        title="Percent",
    )
    mp.postprocess(filename="261014.png")


if __name__ == "__main__":
    main()
