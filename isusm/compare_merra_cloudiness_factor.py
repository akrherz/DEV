"""
Plot a comparison of MERRA Cloudiness Factor
"""

import datetime

import numpy
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
from scipy import stats

ISUAG = get_dbconn("isuag")
icursor = ISUAG.cursor()
COOP = get_dbconn("coop")
ccursor = COOP.cursor()

nt = NetworkTable("ISUAG")


def do(station):
    """Do."""
    csite = nt.sts[station]["climate_site"]
    data = {}
    icursor.execute(
        "SELECT valid, c80 from daily where c80 > 0 and station = %s",
        (station,),
    )
    for row in icursor:
        # convert to MJ dy
        data[row[0]] = float(row[1]) * 41840.0 / 1000000.0

    obs = []
    model = []
    minvalid = datetime.date(2013, 3, 1)
    maxvalid = datetime.date(1980, 1, 1)
    # merra_srad cs is gone
    ccursor.execute(
        """SELECT day, merra_srad from
      alldata_ia where merra_srad > 0
      and station = %s """,
        (csite,),
    )
    for row in ccursor:
        if row[0] in data:
            cs = float(row[2])
            obs.append((cs - data[row[0]]) / cs)
            model.append((cs - float(row[1])) / cs)
            if row[0] < minvalid:
                minvalid = row[0]
            if row[0] > maxvalid:
                maxvalid = row[0]

    if len(obs) < 10:
        return
    obs = numpy.array(obs)
    model = numpy.array(model)

    (fig, ax) = plt.subplots(1, 1)
    bias = numpy.average((model - obs))
    h_slope, intercept, h_r_value, _p_value, _std_err = stats.linregress(
        model, obs
    )
    ax.scatter(model, obs, color="tan", edgecolor="None")
    ax.set_xlabel("MERRA Grid Extracted Cloudiness Factor")
    ax.set_ylabel("ISUAG Observation Cloudiness Factor")
    ax.set_title(
        "%s Daily Solar Radiation Comparison (%s-%s)"
        % (
            nt.sts[station]["name"],
            minvalid.strftime("%-d %b %Y"),
            maxvalid.strftime("%-d %b %Y"),
        )
    )
    ax.plot([0, 1], [0, 1], lw=3, color="r", zorder=2, label="1to1")
    # ax.plot([0,800], [0-bias,800-bias], lw=3,color='k', zorder=2,
    # label='model bias = %.1f' % (bias,))
    ax.plot(
        [0, 1],
        [intercept, intercept + 1.0 * h_slope],
        color="g",
        lw=3,
        zorder=2,
        label=r"Fit: $R^2 = %.2f$" % (h_r_value**2,),
    )
    ax.legend(loc=2)
    ax.set_xlim(-0.4, 1.2)
    ax.set_ylim(-0.4, 1.2)

    fig.savefig(
        "/tmp/merra/%s.png" % (nt.sts[station]["name"].replace(" ", "_"),)
    )
    del fig
    print("%-20s %.2f %.2f" % (nt.sts[station]["name"], bias, h_r_value**2))


for sid in nt.sts.keys():
    do(sid)
