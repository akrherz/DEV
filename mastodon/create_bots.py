"""Create the bot accounts."""

import random
import string

import mastodon
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def generate_random_string(length):
    # Get all the ASCII letters in lowercase and uppercase
    letters = string.ascii_letters
    # Randomly choose characters from letters for the given len of the string
    random_string = "".join(random.choice(letters) for i in range(length))
    return random_string


def main():
    """Go Main Go..."""
    conn = get_dbconn("mesosite")
    cursor = conn.cursor()
    cursor.execute(
        """
        select screen_name, access_token from iembot_mastodon_oauth
        where appid = 2 ORDER by screen_name
        """
    )
    nt = NetworkTable(["WFO", "CWSU"])
    for row in cursor:
        if row[0].find("_") == -1:
            continue
        wfo = row[0].split("_")[1].upper()
        if wfo not in nt.sts:
            print(f"Unknown {row[0]}")
            location = wfo
        else:
            location = "%s, %s" % (nt.sts[wfo]["name"], nt.sts[wfo]["state"])
        desc = (
            f"Syndication of National Weather Service Office {location}. "
            "Unmonitored, contact @akrherz who developed this."
        )
        m = mastodon.Mastodon(
            api_base_url="https://masto.globaleas.org",
            access_token=row[1],
        )
        m.account_update_credentials(
            note=desc,
        )


if __name__ == "__main__":
    main()
