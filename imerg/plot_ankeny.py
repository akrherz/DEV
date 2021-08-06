"""Plot 30 June 2018 rates."""
import datetime

from pyiem.plot import figure_axes

BASE = datetime.datetime(2018, 6, 30)


def reader(fn):
    """Do the work."""
    valids = []
    rates = []
    accums = []
    lvalid = None
    laccum = None
    for line in open(fn):
        tokens = line.strip().split()
        if len(tokens) < 2:
            continue
        ts = tokens[0].split(".")
        accum = float(tokens[1])
        valid = BASE.replace(
            hour=int(ts[0]),
            minute=int(float(ts[1]) / 100.0 * 60.0),
        )
        if lvalid is not None:
            valids.append(valid)
            # mm/s to mm/hr
            rates.append(
                (accum - laccum) / (valid - lvalid).total_seconds() * 3600.0
            )
            accums.append(accum)
        lvalid = valid
        laccum = accum
    return valids, rates, accums


def main():
    """Go Main Go."""
    imerg_valid, imerg_rates, imerg_accum = reader("ankeny_imerg.txt")
    dep_valid, dep_rates, dep_accum = reader("ankeny_dep.txt")

    fig, ax = figure_axes(
        logo="dep",
        title="Ankeny, IA (41.74N 93.59W) :: Evening of 30 June 2018",
    )
    ax.plot(dep_valid, dep_rates, color="b", label="DEP/MRMS")
    ax.plot(imerg_valid, imerg_rates, color="r", label="IMERG")
    ax.grid(True)
    ax.set_ylabel("Precipitation Rate (mm/hr) [solid line]")
    ax.set_xlabel("Local Valid Time (CDT)")

    ax2 = ax.twinx()
    ax2.plot(dep_valid, dep_accum, linestyle="-.", color="b")
    ax2.plot(imerg_valid, imerg_accum, linestyle="-.", color="r")
    ax2.set_ylabel("Total Accumulation (mm) [dashed line]")
    ax.legend(loc=2)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
