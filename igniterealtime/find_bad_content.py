"""Figure out what cruft within Jive is causing API crashes"""
from __future__ import print_function
import sys

import requests

API = "https://igniterealtime.jiveon.com/api/core/v3"
JIVEUSER = "akrherz"
JIVEPASS = sys.argv[1]


def apiget(url):
    """Get what we need"""
    try:
        req = requests.get(url, auth=(JIVEUSER, JIVEPASS))
        if req.status_code != 200:
            print("%s resulted in status %s" % (url, req.status_code))
            return None
        return req.json()
    except Exception as exp:
        print(url)
        print(exp)


def debug(placeid, startindex):
    """Step through this to find the trouble"""
    for i in range(100):
        _index = startindex + i
        url = ("%s/places/"
               "%s/contents?fields=-author&filter=status(published)&"
               "sort=dateCreatedAsc&count=1&startIndex=%s"
               ) % (API, placeid, _index)
        data = apiget(url)
        if data is None:
            continue
        item = data['list'][0]
        print(("    i: %s id: %s type: %s published: %s subject: %s"
               ) % (i, item['id'], item['type'], item['published'],
                    item.get('subject')))


def main():
    """Go main"""
    url = ("%s/places?fields=placeID,name,-resources&"
           "startIndex=0&count=100"
           ) % (API, )
    places = apiget(url)
    for counter, place in enumerate(places['list']):
        placeid = place["placeID"]
        print(("Processing %s typeCode: %s id: %s counter: %s"
               ) % (place['name'], place["typeCode"],
                    place["id"], counter))
        startindex = 0
        chunk = 100
        while startindex > -1:
            print("    running startindex: %s" % (startindex, ))
            url = ("%s/places/"
                   "%s/contents?fields=-author&filter=status(published)&"
                   "sort=dateCreatedAsc&count=100&startIndex=%s"
                   ) % (API, placeid, startindex)
            data = apiget(url)
            if data is None:
                debug(placeid, startindex)
                startindex += chunk
                continue
            startindex += chunk
            if len(data['list']) != chunk:
                print("    Done")
                startindex = -1


if __name__ == '__main__':
    main()
