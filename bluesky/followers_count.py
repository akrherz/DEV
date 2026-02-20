"""Figure out the followers count."""

import os

import atproto
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot, get_cmap
from tqdm import tqdm


def get_followers_count():
    """Do the work."""
    nt = NetworkTable("WFO")
    with get_sqlalchemy_conn("iembot") as conn:
        res = conn.execute(
            sql_helper(
                "select app_pass from iembot_atmosphere_accounts "
                "where handle = 'dmx.weather.im'"
            )
        )
        app_pass = res.first()[0]
        df = pd.read_sql(
            sql_helper("""
            SELECT handle from iembot_atmosphere_accounts
            where iem_owned ORDER by handle ASC
            """),
            conn,
            index_col="handle",
        )
    client = atproto.Client()
    client.login("dmx.weather.im", app_pass)

    for screen_name in tqdm(df.index.values):
        wfo = screen_name[:3].upper()
        if wfo in ["GUM", "HFO", "AFG", "AFC", "AJK"]:
            wfo = f"P{wfo}"
        if wfo == "SJU":
            wfo = "TJSJ"
        try:
            df.at[screen_name, "wfo"] = wfo[-3:]
            df.at[screen_name, "count"] = client.get_profile(
                screen_name
            ).followers_count
            df.at[screen_name, "is_wfo"] = wfo in nt.sts
            print(f"{screen_name}[{wfo}] -> {df.at[screen_name, 'count']}")
        except Exception:
            print(f"{wfo} failed")
    df = df.fillna(0)
    return df


def main():
    """Go Main Go."""
    if not os.path.isfile("followers.csv"):
        df = get_followers_count()
        df.to_csv("followers.csv")
    df = pd.read_csv("followers.csv").set_index("handle")
    mp = MapPlot(
        sector="nws",
        title="BlueSky Followers Count (20 Feb 2026)",
        subtitle=f"Total: {df['count'].sum():,.0f}",
        twitter=True,
        nocaption=True,
    )
    cmap = get_cmap("jet")
    levels = (
        df["count"].quantile([0, 0.1, 0.25, 0.5, 0.75, 0.9]).values.astype(int)
    )
    levels[0] = 1
    data = (
        df.loc[df["is_wfo"] & (df["count"] > 0)].reset_index().set_index("wfo")
    )
    mp.fill_cwas(
        data["count"].to_dict(),
        bins=levels,
        cmap=cmap,
        units="count",
        ilabel=True,
        lblformat="%.0f",
        extend="max",
        spacing="proportional",
        labelbuffer=0,
    )
    txt = "Top 20 Non-WFO\n"
    for sn, row in (
        df.loc[~df["is_wfo"] & (df["count"] > 0)]
        .sort_values("count", ascending=False)
        .head(20)
        .iterrows()
    ):
        txt += f"{sn.split('.')[0]} {row['count']:,.0f}\n"
    mp.panels[0].ax.text(
        0.86,
        0.12,
        txt[:-1],
        transform=mp.panels[0].ax.transAxes,
        bbox=dict(color="w"),
    )
    mp.fig.savefig("followers.png")


if __name__ == "__main__":
    main()
