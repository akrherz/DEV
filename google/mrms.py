"""A frontend to allow scraping of the Google Drive MRMS folder."""
import re

from pyiem.cscap_utils import get_driveclient, get_config
from paste.request import parse_formvars

RESOURCE_REGEX = re.compile(
    "^20[0-9][0-9]/[0-1][0-9]/[0-3][0-9]/20[0-9][0-9][0-1][0-9][0-3][0-9]"
    "[0-2][0-9].zip$"
)


def get_file(drive, parentid, filename):
    """Get the item."""
    res = (
        drive.files()
        .list(q=(f"'{parentid}' in parents and " f"title = '{filename}'"))
        .execute()
    )
    return res["items"][0]


def get_folderid(drive, parentid, foldername):
    """Get the folderid."""
    if parentid is None:
        parentid = "1JCajASK61bFp9h3khOb9PjoS04Um0DfQ"
    res = (
        drive.files()
        .list(q=(f"'{parentid}' in parents and " f"title = '{foldername}'"))
        .execute()
    )
    return res["items"][0]["id"]


def get_resource(drive, resource):
    """Get the resource."""
    (year, month, day, zipfn) = resource.split("/")
    year_folder = get_folderid(drive, None, year)
    month_folder = get_folderid(drive, year_folder, month)
    day_folder = get_folderid(drive, month_folder, day)
    return get_file(drive, day_folder, zipfn)


def application(environ, start_response):
    """Entry."""
    config = get_config()
    drive = get_driveclient(config, "cscap")

    form = parse_formvars(environ)
    resource = form.get("q", "")
    if RESOURCE_REGEX.match(resource):
        item = get_resource(drive, resource)
        start_response(
            "301 Moved Permanently", [("Location", item["downloadUrl"])]
        )
        return [b""]

    start_response("200 OK", [("Content-type", "text/html")])

    return [b"Hello World!"]
