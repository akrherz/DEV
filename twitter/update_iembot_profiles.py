"""Need to set a profile string for my bots."""

import twitter
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, get_properties

PROPS = get_properties()


def main():
    """Go Main Go."""
    nt = NetworkTable(["WFO", "CWSU"])
    df = read_sql(
        """
    SELECT screen_name, access_token, access_token_secret
    from iembot_twitter_oauth
    WHERE access_token is not null
    """,
        get_dbconn("mesosite"),
        index_col="screen_name",
    )

    wfos = list(nt.sts.keys())
    wfos.sort()
    for wfo in wfos:
        username = "iembot_%s" % (wfo.lower()[-3:],)
        if username not in df.index:
            print("%s is unknown?" % (username,))
            continue
        api = twitter.Api(
            consumer_key=PROPS["bot.twitter.consumerkey"],
            consumer_secret=PROPS["bot.twitter.consumersecret"],
            access_token_key=df.at[username, "access_token"],
            access_token_secret=df.at[username, "access_token_secret"],
        )

        location = "%s, %s" % (nt.sts[wfo]["name"], nt.sts[wfo]["state"])
        desc = (
            "Syndication of National Weather Service Office %s. "
            "Unmonitored, contact @akrherz who developed this."
        ) % (location,)
        print("len(desc) = %s" % (len(desc),))
        profileURL = "https://mesonet.agron.iastate.edu/projects/iembot/"
        twuser = api.UpdateProfile(
            description=desc, profileURL=profileURL, location=location
        )
        # twuser.AsDict()['followers_count']
        print("%s %s" % (username, location))


if __name__ == "__main__":
    main()
