"""Get details on attachments in SBS"""
from __future__ import print_function
import sys
import json
import os

import requests

API = "https://igniterealtime.jiveon.com/api/core/v3"
JIVEUSER = sys.argv[1]
JIVEPASS = sys.argv[2]


def apiget(url):
    """Get what we need"""
    try:
        req = requests.get(url, auth=(JIVEUSER, JIVEPASS))
        if req.status_code != 200:
            print("%s resulted in status %s" % (url, req.status_code))
            return {"list": []}
        return req.json()
    except Exception as exp:
        print(url)
        print(exp)


def save_attachments(item):
    """Save what we have for the attachment"""
    if not item.get("attachments", []):
        return
    fn = "attachments/%s_%s.json" % (item["type"], item["id"])
    if os.path.isfile(fn):
        print("    Dup? %s" % (fn,))
    fp = open(fn, "w")
    json.dump(item, fp)
    fp.close()


def main():
    """Go"""
    # Get space details
    url = (
        "%s/places?fields=placeID,name,-resources&" "startIndex=0&count=100"
    ) % (API,)
    places = apiget(url)
    for place in places["list"][8:]:
        placeid = place["placeID"]
        print(
            "Processing %s typeCode: %s id: %s"
            % (place["name"], place["typeCode"], place["id"])
        )
        startindex = 0
        while startindex > -1:
            print("    running startindex: %s" % (startindex,))
            url = (
                "%s/places/"
                "%s/contents?filter=status(published)&"
                "sort=dateCreatedDesc&count=100&startIndex=%s"
            ) % (API, placeid, startindex)
            data = apiget(url)
            startindex += 100
            if len(data["list"]) != 100:
                startindex = -1
            for item in data["list"]:

                save_attachments(item)

                if "comments" in item["resources"]:
                    url = item["resources"]["comments"]["ref"] + "?count=100"
                    # print(url)
                    data2 = apiget(url)
                    for item2 in data2["list"]:
                        save_attachments(item2)

                if "messages" in item["resources"]:
                    url = item["resources"]["messages"]["ref"] + "?count=100"
                    # print(url)
                    data2 = apiget(url)
                    for item2 in data2["list"]:
                        save_attachments(item2)


if __name__ == "__main__":
    main()
