"""Create HTML and resources to drive an autoplot overview page."""

from io import StringIO

import httpx
from bs4 import BeautifulSoup
from pyiem.util import logger
from tqdm import tqdm

LOG = logger()
BASEURL = "http://mesonet.agron.iastate.edu/plotting/auto"
STORAGE = "/mesonet/share/pickup/autoplot"


def write_html(html, plot, meta, counter):
    """Write HTML."""
    desc = meta["description"]
    if len(desc) > 120:
        # careful of dangling HTML tags :(
        with StringIO(" ".join(desc.split()[:30])) as sio:
            desc = BeautifulSoup(sio, "lxml").text
    html.write(
        '<div class="col-md-3 mb-3">'
        '<div class="card h-100">'
        '<div class="card-body">'
        f'<a href="/plotting/auto/?q={plot["id"]}" '
        'class="text-decoration-none">'
        f'<h5 class="card-title">#{plot["id"]}. {plot["label"]}</h5></a>'
        f'<a href="/plotting/auto/?q={plot["id"]}">'
        f'<img src="/pickup/autoplot/{plot["id"]}_thumb.png" '
        f'class="img-fluid mb-2" alt="Plot {plot["id"]} thumbnail"></a>'
        f'<p class="card-text">{desc}</p>'
        "</div></div></div>\n"
    )
    if counter % 4 == 0:
        html.write('</div><!-- ./row --><div class="row g-3">\n')


def main():
    """Go Main Go."""
    html = StringIO()
    # 1. get general metadata for all autoplots
    entries = httpx.get(f"{BASEURL}/meta/0.json", timeout=30).json()

    counter = 1
    # for each entry
    for section in entries["plots"]:
        if counter > 1:
            html.write("</div>\n")
        counter = 1
        html.write(f"<h2>{section['label']}</h2>\n")
        html.write('<div class="row g-3">\n')
        progress = tqdm(section["options"])
        for plot in progress:
            apid = plot["id"]
            progress.set_description(str(apid))
            # 2. get a thumbnail image result (when possible)
            uri = f"{BASEURL}/plot/{apid}/dpi:50::_r:43::_gallery:1.png"
            # HACK
            if apid == 205:
                uri = (
                    f"{uri[:-4]}::_opt_max_tmpf_above:on::"
                    "max_tmpf_above:90.png"
                )
            req = httpx.get(uri, timeout=300)
            if req.status_code != 200:
                LOG.info("got %s status_code from %s", req.status_code, uri)
                continue
            with open(f"{STORAGE}/{apid}_thumb.png", "wb") as fh:
                fh.write(req.content)
            # 3. get autoplot metadata to drive an info box
            meta = httpx.get(f"{BASEURL}/meta/{apid}.json", timeout=30).json()
            write_html(html, plot, meta, counter)
            counter += 1

    with open(f"{STORAGE}/overview.html", "w", encoding="utf-8") as fh:
        fh.write('<div class="container-fluid">\n')
        fh.write('<div class="row g-3">\n')
        fh.write(html.getvalue())
        fh.write("</div></div>")


if __name__ == "__main__":
    main()
