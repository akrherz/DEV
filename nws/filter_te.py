"""Need to filter the raw tornado emergency file"""


def main():
    """Go Main Go"""
    output = open('tornado_emergency_filtered.txt', 'wb')
    good = 0
    for report in open('tornado_emergency.txt', 'rb').read().split(b"\003"):
        raw = b" ".join(
            report.upper().replace(b"\r", b"").replace(b"\n", b" ").split())
        if raw.find(b"ACTUAL TORNADO EMERGENCY") > 0:
            print('hit')
            continue
        elif raw.find(b"THEIR TORNADO EMERGENCY") > 0:
            print('hit')
            continue
        elif raw.find(b"YOUR TORNADO EMERGENCY") > 0:
            print('hit')
            continue
        elif raw.find(b"TEST TORNADO WARNING") > 0:
            print('hit')
            continue
        elif raw.find(b"THIS IS A TEST MESSAGE") > 0:
            print('hit')
            continue
        good += 1
        output.write(report + b"\003")
    print("Filtered Products %s" % (good, ))
    output.close()


if __name__ == '__main__':
    main()
