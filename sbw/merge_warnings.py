"""Add warning information to a CSV file."""
import datetime

import requests
import pandas as pd

IEM_WEB = (
    "https://mesonet.agron.iastate.edu/json/sbw_by_point.py?lon=%s&"
    "lat=%s&valid=%s"
)


def main():
    """Go Main Go."""
    df = pd.read_csv("intensetors.csv")
    # Make valid timestamp for database usage
    df["timestampUTC"] = pd.to_datetime(
        df["date"] + " " + df["CST"], format="%y-%m-%d %H:%M:%S"
    ) + datetime.timedelta(hours=6)
    # Addition columns that we are going to provide
    for colname in [
        "first_motion_drct",
        "first_motion_sknt",
        "first_torwarn_link",
    ]:
        df[colname] = None
    # Loop over the tors
    for idx, row in df.iterrows():
        dt = row["timestampUTC"].strftime("%Y-%m-%dT%H:%MZ")
        # Go find storm based warnings via IEM web service
        req = requests.get(IEM_WEB % (row["slon"], row["slat"], dt))
        # create dataframe from the result
        sbws = pd.DataFrame(req.json()["sbws"])
        if sbws.empty:
            continue
        sbws["issue"] = pd.to_datetime(sbws["issue"])
        torwarns = sbws[sbws["phenomena"] == "TO"]
        if not torwarns.empty:
            trow = torwarns.iloc[0]
            df.at[idx, "first_torwarn_link"] = (
                "https://mesonet.agron.iastate.edu/vtec/f/%s"
                "-O-NEW-K%s-TO-W-%04i"
            ) % (trow["issue"].year, trow["wfo"], trow["eventid"])
        else:
            trow = sbws.iloc[0]
        df.at[idx, "first_motion_drct"] = trow["tml_direction"]
        df.at[idx, "first_motion_sknt"] = trow["tml_sknt"]

    df.to_csv("results.csv")


if __name__ == "__main__":
    main()
