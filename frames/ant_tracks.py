"""Simple."""

import httpx
import pandas as pd
from tqdm import tqdm


def main():
    """Go Main Go."""
    series = pd.date_range("2025/02/06 13:00", "2025/02/06 18:00", freq="300S")
    progress = tqdm(series)
    i = 313
    for now in progress:
        progress.set_description(f"{now:%Y%m%d %H%M}")
        uri = now.strftime(
            "http://mesonet.agron.iastate.edu/roads/iem.php?"
            "trucks&nexrad&valid=%Y-%m-%d%%20%H:%M"
        )
        resp = httpx.get(uri, timeout=60)
        with open(f"images/{i:05.0f}.png", "wb") as fh:
            fh.write(resp.content)
        i += 1


if __name__ == "__main__":
    main()
