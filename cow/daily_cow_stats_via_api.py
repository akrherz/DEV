"""Call IEM Cow API to get daily cow stats."""

import httpx

import pandas as pd


def main():
    """Go Main Go."""
    rows = []
    for dt in pd.date_range("2024/01/01", "2024/06/10", freq="D"):
        dtend = dt + pd.Timedelta(days=1)
        # Get a 6z to 6z period
        url = (
            "https://mesonet.agron.iastate.edu/api/1/cow.json?"
            f"begints={dt:%Y-%m-%d}T06:00Z&endts={dtend:%Y-%m-%d}T06:00Z&"
            "phenomena=SV&phenomena=TO&"
            # to limit to certain WFOs, add this to the URL
            # "wfo=DMX&wfo=EAX&wfo=TOP&wfo=OAX&wfo=ICT&wfo=SGF&wfo=LSX&" etc
        )
        stats = httpx.get(url, timeout=300).json()["stats"]
        stats["date"] = dt
        rows.append(stats)
    pd.DataFrame(rows).to_csv("cow_stats.csv", index=False)


if __name__ == "__main__":
    main()
