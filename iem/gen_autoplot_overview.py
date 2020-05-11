"""Create HTML and resources to drive an autoplot overview page."""
from io import StringIO

from bs4 import BeautifulSoup
from pyiem.util import logger
from tqdm import tqdm
import requests

LOG = logger()
BASEURL = "http://iem.local/plotting/auto"
STORAGE = "/mesonet/share/pickup/autoplot"


def write_html(html, plot, meta, counter):
    """Write HTML."""
    desc = meta["description"]
    if len(desc) > 120:
        # careful of dangling HTML tags :(
        desc = " ".join(desc.split()[:30])
        desc = BeautifulSoup(desc, "lxml").text
    html.write(
        f'<div class="col-md-3 well">'
        f'<a href="/plotting/auto/?q={plot["id"]}">'
        f'<h4>#{plot["id"]}. {plot["label"]}</h4></a>'
        f'<a href="/plotting/auto/?q={plot["id"]}">'
        f'<img src="/pickup/autoplot/{plot["id"]}_thumb.png" '
        f'class="img img-responsive"></a><br>{desc}'
        "</div>\n"
    )
    if counter % 4 == 0:
        html.write('</div><!-- ./row --><div class="row">\n')


def main():
    """Go Main Go."""
    html = StringIO()
    # 1. get general metadata for all autoplots
    entries = requests.get(f"{BASEURL}/meta/0.json").json()

    counter = 1
    # for each entry
    for section in entries["plots"]:
        if counter > 1:
            html.write("</div>\n")
        counter = 1
        html.write(f'<h2>{section["label"]}</h2>\n')
        html.write('<div class="row">\n')
        progress = tqdm(section["options"])
        for plot in progress:
            apid = plot["id"]
            progress.set_description(str(apid))
            # 2. get a thumbnail image result (when possible)
            uri = f"{BASEURL}/plot/{apid}/dpi:50.png"
            req = requests.get(uri)
            if req.status_code != 200:
                LOG.info("got %s status_code from %s", req.status_code, uri)
                continue
            with open(f"{STORAGE}/{apid}_thumb.png", "wb") as fh:
                fh.write(req.content)
            # 3. get autoplot metadata to drive an info box
            meta = requests.get(f"{BASEURL}/meta/{apid}.json").json()
            write_html(html, plot, meta, counter)
            counter += 1

    with open(f"{STORAGE}/overview.html", "w") as fh:
        fh.write('<div class="row">\n')
        fh.write(html.getvalue())
        fh.write("</div>")


if __name__ == "__main__":
    main()
