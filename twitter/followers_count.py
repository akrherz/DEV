"""Need to set a profile string for my bots."""

from tqdm import tqdm
import twitter
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot, get_cmap, pretty_bins
from pyiem.util import get_dbconn, get_properties, get_sqlalchemy_conn


def main():
    """Go Main Go."""
    nt = NetworkTable("WFO")
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            "SELECT screen_name from iembot_twitter_oauth where iem_owned "
            "ORDER by screen_name ASC",
            conn,
            index_col="screen_name",
        )

    props = get_properties()
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT access_token, access_token_secret from iembot_twitter_oauth "
        "WHERE screen_name = 'akrherz'"
    )
    row = cursor.fetchone()
    api = twitter.Api(
        consumer_key=props["bot.twitter.consumerkey"],
        consumer_secret=props["bot.twitter.consumersecret"],
        access_token_key=row[0],
        access_token_secret=row[1],
    )
    for screen_name in tqdm(df.index.values):
        wfo = screen_name.split("_")[1].upper()
        if wfo in ["GUM", "HFO", "AFG", "AFC", "AJK"]:
            wfo = f"P{wfo}"
        if wfo == "JSJ":
            wfo = "TJSJ"
        try:
            res = api.GetUser(screen_name=screen_name)
            df.at[screen_name, "wfo"] = wfo[-3:]
            df.at[screen_name, "count"] = res.followers_count
            df.at[screen_name, "is_wfo"] = wfo in nt.sts
        except Exception:
            print(f"{wfo} failed")
    df = df.fillna(0)
    print(df)
    mp = MapPlot(
        sector="nws",
        title="IEMBOT Followers Count (6 Jul 2022)",
        subtitle=f"Total: {df['count'].sum():,.0f}",
        twitter=True,
    )
    cmap = get_cmap("jet")
    levels = list(range(0, 1601, 200))
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
        extend="neither",
        labelbuffer=0,
    )
    y = 0.65
    for sn, row in (
        df.loc[~df["is_wfo"] & (df["count"] > 0)]
        .sort_values("count", ascending=False)
        .iterrows()
    ):
        mp.panels[0].ax.text(
            0.86,
            y,
            f"{sn}  {row['count']:,.0f}",
            transform=mp.panels[0].ax.transAxes,
            bbox=dict(color="w"),
        )
        y -= 0.05
        if y < 0.2:
            break
    mp.fig.savefig("followers.png")


if __name__ == "__main__":
    main()
