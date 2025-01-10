"""Build redirect mappings for the following community URIs

/thread/%s    <-- this is the "id" in the base messages
/messages/%s
/docs/%s

Old Jive types:
  discussion "discussion_id" -> to get post to add to message map
  post  "post_id" -> to get post
  document  "document_id" -> to get post
  message   "id" -> to get post

Redo:
  Openfire Support at 9600
  Community Plugins at 100

"""

import sys

import psycopg2
import requests

DIS = "https://discourse.igniterealtime.org"
JIVEUSER = sys.argv[1]
JIVEPASS = sys.argv[2]
API = "https://igniterealtime.jiveon.com/api/core/v3"
MAP_FPS = {
    "thread": open("thread_mapping.txt", "a", encoding="utf-8"),
    "messages": open("message_mapping.txt", "a", encoding="utf-8"),
    "docs": open("docs_mapping.txt", "a", encoding="utf-8"),
    "blogs": open("blogs_mapping.txt", "a", encoding="utf-8"),
}


def save_item(item, xref):
    """Do the magic"""
    if item["type"] in ["message", "comment"]:
        # Just need to map the IDs
        key = item["id"]
        target = xref.get(key)
        if target is None:
            print("    Uh oh, unknown key: %s" % (key,))
            return
        MAP_FPS["messages"].write("%s %s\n" % (key, target))
    elif item["type"] == "discussion":
        # map thread
        threadid = item["id"]
        key = "%s_%s" % (item["type"], threadid)
        target = xref.get(key)
        if target is None:
            print("    Uh oh, unknown key: %s" % (key,))
            return
        MAP_FPS["thread"].write("%s %s\n" % (threadid, target))
        # map message id via a hack
        messageid = item["resources"]["editHTML"]["ref"].split("/")[-2]
        # print(json.dumps(item, indent=4))
        MAP_FPS["messages"].write("%s %s\n" % (messageid, target))
    elif item["type"] == "post":
        # map thread
        key = "%s_%s" % (item["type"], item["id"])
        target = xref.get(key)
        if target is None:
            print("    Uh oh, unknown key: %s" % (key,))
            return
        MAP_FPS["messages"].write("%s %s\n" % (item["id"], target))
        # do blog aspect now too
        url = "/".join(item["resources"]["html"]["ref"].split("/")[4:])
        MAP_FPS["blogs"].write("%s %s\n" % (url, target))
    elif item["type"] == "document":
        key = "%s_%s" % (item["type"], item["id"])
        target = xref.get(key)
        if target is None:
            print("    Uh oh, unknown key: %s" % (key,))
            return
        docid = item["resources"]["editHTML"]["ref"].split("/")[-2]
        MAP_FPS["docs"].write("%s %s\n" % (docid, target))
    elif item["type"] in ["poll", "person", "2901"]:
        pass
    else:
        print("    Unknown type: %s" % (item["type"],))
        # print(json.dumps(item, indent=4))
        # sys.exit()


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


def build_xref():
    """Cross reference"""
    pgconn = psycopg2.connect(database="discourse")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        SELECT distinct post_id, value from post_custom_fields
        WHERE name = 'import_id'
    """
    )
    xref = {}
    for row in cursor:
        xref[row[1]] = row[0]
    return xref


def main():
    """Go Main Go"""
    xref = build_xref()
    url = (
        "%s/places?fields=placeID,name,-resources&startIndex=0&count=100"
    ) % (API,)
    places = apiget(url)
    for counter, place in enumerate(places["list"]):
        placeid = place["placeID"]
        # if place['name'] != 'Community Plugins':
        #    continue
        print(
            ("Processing %s typeCode: %s id: %s counter: %s")
            % (place["name"], place["typeCode"], place["id"], counter)
        )
        startindex = 0
        while startindex > -1:
            print("    running startindex: %s" % (startindex,))
            url = (
                "%s/places/"
                "%s/contents?fields=-author&filter=status(published)&"
                "sort=dateCreatedAsc&count=100&startIndex=%s"
            ) % (API, placeid, startindex)
            data = apiget(url)
            startindex += 100
            if len(data["list"]) != 100:
                startindex = -1
            for item in data["list"]:
                save_item(item, xref)
                if "comments" in item["resources"]:
                    url = item["resources"]["comments"]["ref"] + "?count=100"
                    data2 = apiget(url)
                    for item2 in data2["list"]:
                        save_item(item2, xref)
                if "messages" in item["resources"]:
                    url = item["resources"]["messages"]["ref"] + "?count=100"
                    data2 = apiget(url)
                    for item2 in data2["list"]:
                        save_item(item2, xref)

    for key in MAP_FPS:
        MAP_FPS[key].close()


if __name__ == "__main__":
    main()
