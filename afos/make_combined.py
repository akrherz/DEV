import os
import re

import pandas as pd
from pyiem.util import noaaport_text

WMO_RE = re.compile("^U..... .... [\d]{6}$")


def normalize(text):
    """Fix problems :/"""
    text = text.replace("\x1e", "").replace("\000", "").replace("\r", "")
    lines = []
    for line in text.split("\n"):
        if WMO_RE.match(line):
            lines.append("\n\n")
        if line.find("=U") > -1:
            line = line[: line.find("=U")] + "="
        if line.find("KDENUB") > -1:
            line = line[(line.find("KDEN") + 4) :]
        elif line.find("@") > -1:
            continue
        lines.append(line)
    return "\n".join(lines)


for dt in pd.date_range("2000/01/01", "2015/01/20"):
    # for dt in pd.date_range('2008/08/14', '2008/08/14'):
    cfn = f"combined/{dt:%Y%m%d}.txt"
    if os.path.isfile(cfn):
        os.remove(cfn)
    for mydir in (
        "cybg  cyeg  cyka  cyqb  cyqu  cyrt  cyxt  cyyf  cyzf  kwbc cydf  "
        "cyev  cype  cyqr  cyqx  cyxj  cyxu  cyyr  cyzv  kmsc"
    ).split():
        fn = f"{mydir}/{dt:%Y%m%d}.txt"
        if not os.path.isfile(fn):
            continue
        with open(fn, "rb") as fh:
            tokens = normalize(fh.read().decode("ascii", "ignore")).split(
                "\n\n"
            )
        with open(cfn, "a") as fh:
            for token in tokens:
                meat = token.strip()
                if len(meat) < 10:
                    continue
                fh.write(noaaport_text(meat))
