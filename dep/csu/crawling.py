"""Crawl before we walk here."""

import json

import requests


def main():
    """Go Main Go."""
    resp = requests.post(
        "http://csip.engr.colostate.edu:8084/csip-crlmod/d/operation/5.0",
        headers={"User-Agent": "Daily Erosion Project / daryl"},
        timeout=10,
        json={
            "parameter": [
                {"name": "native_formats", "value": "TRUE"},
                {"name": "keywords", "value": "Corn"},
                {"name": "limit", "value": "all"},
                # {"name":"id","value":["22693"]},
            ]
        },
    )
    if resp.status_code != 200:
        print(resp.status_code)
        print(resp.content)
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=4))


if __name__ == "__main__":
    main()
