"""Need to set a profile string for my bots."""

import time

import twitter
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
    maxval = 0
    max10k = 0
    for wfo in list(nt.sts.keys())[:]:
        if len(wfo) == 4:
            wfo = wfo[1:]
        name = f"iembot_{wfo.lower()}"
        try:
            for user in api.GetFollowers(screen_name=name):
                if user.followers_count > maxval:
                    maxval = user.followers_count
                    print(f"Max: {name} -> {user.screen_name} {maxval}")
                if (
                    user.friends_count < 10_000
                    and user.followers_count > max10k
                ):
                    max10k = user.followers_count
                    print(
                        f"Max10k: {name} -> {user.screen_name}"
                        f"[{user.friends_count}] {max10k}"
                    )

        except Exception as exp:
            print(name, "failed", exp)
        time.sleep(7 * 60)


if __name__ == "__main__":
    main()
