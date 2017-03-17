import requests
import sys

PACKAGE = sys.argv[1]
RELEASE = sys.argv[2]

req = requests.get(("https://api.github.com/repos/igniterealtime/%s/"
                    "releases/tags/v%s" % (PACKAGE, RELEASE)))
j = req.json()
total = 0
print("%s Download Stats for Release: %s" % (PACKAGE, RELEASE))
for a in j['assets']:
    print("%27s %6i" % (a['name'], a['download_count']))
    total += a['download_count']
print("%27s ======" % ("", ))
print("%27s %6i" % ("", total))
