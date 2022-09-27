"""figure out US landfalls in hurdat2"""


def main():
    """Go Main Go"""
    lastcane = ""
    with open("gc_dates.txt", "w", encoding="ascii") as fp:
        with open("hurdat2-1851-2021-041922.txt", encoding="ascii") as fh:
            for line in fh:
                tokens = line.split(",")
                if len(tokens) < 10:
                    cane = tokens[0]
                    continue
                if (
                    tokens[2].strip() == "L"
                    and tokens[3].strip() == "HU"
                    and cane != lastcane
                ):
                    # S Tip of Florida is 25N -81W
                    lat = float(tokens[4][:-1])
                    lon = 0 - float(tokens[5][:-1])
                    if lat >= 20 and lon < -81:
                        fp.write(f"{tokens[0]}\n")
                        print(f"{cane},{tokens[4]},{tokens[5]}")
                        lastcane = cane
                    else:
                        print(f"DQ {cane},{tokens[4]},{tokens[5]}")


if __name__ == "__main__":
    main()
