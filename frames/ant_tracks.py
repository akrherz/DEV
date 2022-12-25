"""Simple."""

import requests
import pandas as pd
from tqdm import tqdm


def main():
    """Go Main Go."""
    series = pd.date_range("2022/12/21 09:00", "2022/12/25 13:00", freq="300S")
    progress = tqdm(series)
    i = 0
    for now in progress:
        progress.set_description(f"{now:%Y%m%d %H%M}")
        uri = now.strftime(
            "http://mesonet.agron.iastate.edu/roads/iem.php?"
            "trucks&nexrad&valid=%Y-%m-%d%%20%H:%M"
        )
        req = requests.get(uri, timeout=60)
        with open(f"images/{i:05.0f}.png", "wb") as fh:
            fh.write(req.content)
        i += 1


if __name__ == "__main__":
    main()
