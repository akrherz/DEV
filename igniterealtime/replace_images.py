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
import os
import sys

import requests
import psycopg2

APIKEY = open("APIKEY.txt", "r").read().strip()
DIS = "https://discourse.igniterealtime.org"
JIVEUSER = sys.argv[1]
JIVEPASS = sys.argv[2]


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
    pgconn = psycopg2.connect(database="discourse")
    cursor = pgconn.cursor()
    # manually created table by doing a search on posts for certain content
    cursor.execute(
        """
        SELECT id from daryl WHERE id > 165000 ORDER by id ASC
    """
    )
    for row in cursor:
        post_id = row[0]
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
        while True:
            pos = raw.find(
                (
                    "community.igniterealtime.org/"
                    "servlet/JiveServlet/downloadImage"
                )
            )
            if pos == -1:
                break
            pos2 = raw[pos:].find('"')
            url = "https://%s" % (raw[pos : pos + pos2],)

            req = requests.get(url, auth=(JIVEUSER, JIVEPASS))
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

            files = {
                "file": (
                    url.split("/")[-1],
                    open(tmpfn, "rb"),
                    "image/%s" % (url.split(".")[-1],),
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
            print("uploading: %s" % (files["file"][0],))
            req = requests.post(
                "%s/uploads.json" % (DIS,), data=data, files=files
            )
            if req.status_code != 200:
                print("status code is %s" % (res.status_code,))
                print(res.content)
            res = req.json()
            newurl = "discourse.igniterealtime.org%s" % (res["url"])
            raw = raw.replace(raw[pos : pos + pos2], newurl)
            print(newurl)
            print(post_id)
            data = {
                "post[raw]": raw,
                "api_key": APIKEY,
                "api_username": "admin",
            }
            res = requests.put("%s/posts/%s.json" % (DIS, post_id), data=data)
            if res.status_code != 200:
                print(res.status_code)
                print(res.content)
            os.unlink(tmpfn)


if __name__ == "__main__":
    main()
