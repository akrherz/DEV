"""Cheap script to get stats"""
from __future__ import print_function
import sys

import requests


def main(argv):
    """Go Main Go"""
    package = argv[1]
    release = argv[2]
    req = requests.get(("https://api.github.com/repos/igniterealtime/%s/"
                        "releases/tags/v%s" % (package, release)))
    j = req.json()
    total = 0
    print("%s Download Stats for Release: %s" % (package, release))
    for asset in j['assets']:
        print("%33s %6i" % (asset['name'], asset['download_count']))
        total += asset['download_count']
    print("%33s ======" % ("", ))
    print("%33s %6i" % ("", total))


if __name__ == '__main__':
    main(sys.argv)
