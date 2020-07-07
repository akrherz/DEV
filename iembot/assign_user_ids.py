"""Update the database with the user's user_id."""
from pyiem.util import get_dbconn, get_properties
import twitter


def main():
    """Go Main Go."""
    config = get_properties()
    access_token = "..."
    api = twitter.Api(
        consumer_key=config["bot.twitter.consumerkey"],
        consumer_secret=config["bot.twitter.consumersecret"],
        access_token_key=access_token,
        access_token_secret="...",
    )
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute(
        "SELECT screen_name from iembot_twitter_oauth where user_id is null"
    )
    for row in cursor:
        try:
            user_id = api.UsersLookup(screen_name=row[0])[0].id
        except Exception:
            print("FAIL %s" % (row[0],))
            continue
        print("%s -> %s" % (row[0], user_id))
        cursor2.execute(
            """
        UPDATE iembot_twitter_oauth SET user_id = %s where screen_name = %s
        """,
            (user_id, row[0]),
        )
    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
