"""figure out US landfalls in hurdat2"""


def main():
    """Go Main Go"""
    lastcane = ''
    fp = open('dates.txt', 'w')
    for line in open('hurdat2-1851-2017-050118.txt'):
        tokens = line.split(",")
        if len(tokens) < 10:
            cane = tokens[0]
            continue
        if (tokens[2].strip() == 'L' and tokens[3].strip() == 'HU' and
                cane != lastcane):
            # S Tip of Florida is 25N -81W
            lat = float(tokens[4][:-1])
            lon = 0 - float(tokens[5][:-1])
            if lat >= 20 and lon > -81:
                fp.write("%s\n" % (tokens[0], ))
                print("%s,%s,%s" % (cane, tokens[4], tokens[5]))
                lastcane = cane
            else:
                print("DQ %s,%s,%s" % (cane, tokens[4], tokens[5]))
    fp.close()


if __name__ == '__main__':
    main()
