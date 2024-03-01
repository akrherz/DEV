"""Cheap script to get stats"""

import sys

import requests


def main(argv):
    """Go Main Go"""
    package = argv[1]
    release = argv[2]
    req = requests.get(
        f"https://api.github.com/repos/igniterealtime/{package}/"
        f"releases/tags/v{release}",
        timeout=30,
    )
    j = req.json()
    total = 0
    print(f"{package} Download Stats for Release: {release}")
    for asset in j["assets"]:
        print("%38s %6i" % (asset["name"], asset["download_count"]))
        total += asset["download_count"]
    print("%38s ======" % ("",))
    print("%38s %6i" % ("", total))


if __name__ == "__main__":
    main(sys.argv)
