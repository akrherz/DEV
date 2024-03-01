"""Compare our unit conversions."""

# Stdlib
import os
import subprocess
import sys
from string import ascii_uppercase

# Third Party
from pyiem.nws.products.shef import process_message_a

KNOWNS = [
    "MI",  # emailed WHFS, appears to be unitless
    "PC",  # unsure
    "PF",  # unsure what is happening here
    "PL",  # unsure
    "PP",  # unsure
    "PY",  # unsure
    "TC",  # delta_deg
    "TF",  # degree days F
    "TH",  # degree days F, unconvertable
    "TJ",  # delta_degF unconvertable
    "XU",  # emailed WHFS, SHEF manual appears wrong
]


def run(code):
    """See what happens with this code."""
    if code in KNOWNS:
        return
    # Can't use a number invalid for wind direction
    sentinel = 10
    msg = f".AR AESI4 210910 C DH0600/DUS/{code} {sentinel}"
    # See what shefit does
    proc = subprocess.Popen(
        "./shefit",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (stdout, _stderr) = proc.communicate(msg.encode("ascii"))
    res = stdout.decode("ascii")
    if res == "":
        return
    shefit_value = float(res.split()[6])

    res = process_message_a(msg)
    pyiem_value = res[0].to_english()
    if pyiem_value is not None and abs(pyiem_value - shefit_value) < 0.01:
        return
    # Case 1
    if shefit_value == sentinel:
        if pyiem_value is None:
            return
        elif pyiem_value != sentinel:
            print(f"{code}, pyiem: {pyiem_value} shefit has {shefit_value}.")
    else:
        if pyiem_value is None:
            print(f"pyIEM did not handle {code}, shefit has {shefit_value}.")
        elif pyiem_value != sentinel:
            print(f"{code}, pyiem: {pyiem_value} shefit has {shefit_value}.")


def main(argv):
    """Go Main Go."""
    os.chdir("/home/akrherz/projects/pyWWA/shef_workspace/")
    if len(argv) == 2:
        run(argv[1])
        return
    for chr1 in ascii_uppercase:
        for chr2 in ascii_uppercase:
            run(chr1 + chr2)


if __name__ == "__main__":
    main(sys.argv)
