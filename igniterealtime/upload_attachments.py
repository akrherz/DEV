"""Upload Jive attachments as discourse upload

1. build cross reference of posts from Jive to discourse
2. Get the attachment

"status": "published",
"contentType": "image/png",
"name": "asterisk-IM.png",
"typeCode": 13,
"url": "https://community.../api/core/v3/attachments/18541/data",
"doUpload": false,
"type": "attachment",
"id": "18541",
"resources": {
    "self": {
"ref": "https://community.igniterealtime.org/api/core/v3/attachments/18541",
        "allowed": [
            "DELETE",
            "GET"
        ]
    }
},
"size": 27806


3. Upload the attachment
4. Get the discourse post
5. Add link at bottom of post
<img src="/uploads/default/o/5...png" width="375" height="500">

<a class="attachment" href="/uploads/...txt">hello.txt</a> (12 Bytes)
6. Put the new post
"""
from __future__ import print_function
import json
import glob
import os
import sys

import requests
import psycopg2

APIKEY = open("APIKEY.txt", "r").read().strip()
DIS = "https://discourse.igniterealtime.org"
JIVEUSER = "akrherz"
JIVEPASS = sys.argv[1]


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
    files = glob.glob("attachments/*.json")
    files.sort()
    for fn in files:
        item = json.load(open(fn))
        key = (
            "%s_%s" % (item["type"], item["id"])
            if item["type"] in ["discussion", "post", "document"]
            else item["id"]
        )
        if xref.get(key) is None:
            print("failed to xref fn: %s key: %s" % (fn, key))
            continue
        post_id = xref[key]
        print("fn: %s has post_id: %s" % (fn, post_id))
        res = requests.get(
            ("%s/posts/%s.json?api_key=%s&api_username=admin")
            % (DIS, post_id, APIKEY)
        )
        if res.status_code != 200:
            print(res.status_code)
            print(res.content)
        post = res.json()
        raw = post["raw"]
        if len(raw) > 60000:
            print("post is too long!")
            continue
        for attachment in item["attachments"]:
            req = requests.get(attachment["url"], auth=(JIVEUSER, JIVEPASS))
            if req.status_code != 200:
                print(
                    "Download attachment failed with code: %s"
                    % (req.status_code,)
                )
                print(req.content)
                continue
            tmpfn = "%s.bin" % (post_id,)
            fp = open(tmpfn, "wb")
            fp.write(req.content)
            fp.close()

            try:
                attachfilename = (
                    attachment["name"]
                    .decode("utf-8")
                    .encode("ascii", "ignore")
                )
            except Exception as exp:
                attachfilename = "unknown"
            files = {
                "file": (
                    attachfilename,
                    open(tmpfn, "rb"),
                    attachment["contentType"],
                    {"Expires": "0"},
                )
            }
            data = {
                "type": "composer",
                "synchronous": True,
                "user_id": post["user_id"],
                "api_username": post["username"],
                "api_key": APIKEY,
            }
            print("uploading: %s" % (attachment["name"],))
            req = requests.post(
                "%s/uploads.json" % (DIS,), data=data, files=files
            )
            if req.status_code != 200:
                print("status code is %s" % (res.status_code,))
                print(res.content)
            res = req.json()

            if attachment["contentType"].startswith("image"):
                raw += ('\n<img src="%s" ' 'width="%s" height="%s">') % (
                    res["url"],
                    res["width"],
                    res["height"],
                )
            else:
                raw += (
                    '\n<a class="attachment" ' 'href="%s">%s</a> (%s Bytes)'
                ) % (res["url"], attachment["name"], attachment["size"])
            data = {
                "post[raw]": raw,
                "api_key": APIKEY,
                "api_username": "admin",
            }
            res = requests.put("%s/posts/%s.json" % (DIS, post_id), data=data)
            if res.status_code != 200:
                print(res.status_code)
                print(res.content)
            print(
                "%s -> %s"
                % (attachment["name"], res.json()["post"]["updated_at"])
            )
            os.unlink(tmpfn)
        os.rename(fn, fn + ".done")


if __name__ == "__main__":
    main()
