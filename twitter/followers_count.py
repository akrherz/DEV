"""Need to set a profile string for my bots."""

from tqdm import tqdm
import twitter
from pyiem.plot import MapPlot, get_cmap
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, get_properties


def main():
    """Go Main Go."""
    props = get_properties()
    nt = NetworkTable(["WFO"])
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
    data = {}
    total = 0
    for wfo in tqdm(list(nt.sts.keys())[:]):
        if len(wfo) == 4:
            wfo = wfo[1:]
        name = f"iembot_{wfo.lower()}"
        try:
            res = api.GetUser(screen_name=name)
            data[wfo] = res.followers_count
            total += res.followers_count
        except Exception:
            print(f"{wfo} failed")

    mp = MapPlot(
        sector="nws",
        title="IEMBOT Followers Count (25 Feb 2022)",
        subtitle=f"Total: {total:.0f}",
        twitter=True,
    )
    cmap = get_cmap("jet")
    levels = list(range(0, 1001, 100))
    levels[0] = 1
    mp.fill_cwas(
        data,
        bins=levels,
        cmap=cmap,
        units="count",
        ilabel=True,
        lblformat="%.0f",
    )
    mp.fig.savefig("followers.png")


if __name__ == "__main__":
    main()
