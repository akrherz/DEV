"""See if we need to dedup."""

from pyiem.network import Table as NetworkTable


def main():
    """Go Main Go"""
    nt = NetworkTable("RAOB", only_online=False)

    for station in nt.sts:
        if not station.startswith("_"):
            continue
        # Magic
        stations = nt.sts[station]["name"].split("--")[1].strip().split()
        for station2 in stations:
            ab = nt.sts[station2]["archive_begin"]
            ae = nt.sts[station2]["archive_end"]
            on = nt.sts[station2]["online"]
            print(f"{station} {station2}[{on}] {ab} -> {ae}")
        print()


if __name__ == "__main__":
    main()
