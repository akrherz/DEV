"""Generate a nice plot for a feature image of forecast."""
import datetime
import sys

import requests
from metpy.units import units
from metpy.calc import windchill
import pandas as pd
import matplotlib.dates as mdates
from pyiem.plot.use_agg import plt

conf = {
    'ISU': ['#C8102E', '#F1BE48', 41.9904, -93.6185, 'Ames'],
    'UI': ['#FFCD00', '#000000', 41.639, -91.544, 'Iowa City'],
    'UNI': ['#4B116F', '#FFCC00', 42.554, -92.4012, 'Waterloo'],
}

def main(argv):
    """Go Main Go."""
    school = argv[1]
    req = requests.get(
        ('https://api.weather.gov/points/%s,%s/forecast/hourly'
         ) % (conf[school][2], conf[school][3]))
    jdata = req.json()
    rows = []
    for data in jdata['properties']['periods']:
        ts = datetime.datetime.strptime(data['endTime'][:13], '%Y-%m-%dT%H')
        rows.append(
            dict(valid=ts, tmpf=data['temperature'],
                 smph=int(data['windSpeed'].split()[0])))

    df = pd.DataFrame(rows[:-24])
    df['wcht'] = windchill(
        df['tmpf'].values * units('degF'),
        df['smph'].values * units('mph')
    )
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    ax.plot(df['valid'], df['wcht'], lw=2, color='g', label='Wind Chill')
    ax.plot(df['valid'], df['tmpf'], lw=2, color='r', label='Temperature')
    ax.set_ylabel(r"Temperature $^\circ$F")
    ax.set_title(
        ("NWS NDFD Grid Point Forecast for %s Airport"
         ) % (conf[school][4])
    )
    ax.grid(True)
    ax.legend(loc=1, ncol=2)
    ax.set_ylim(-60, 60)
    ax.set_yticks(range(-60, 61, 10))
    ax2 = ax.twinx()
    ax2.scatter(df['valid'].values, df['smph'].values)
    ax2.set_ylim(0, 24)
    ax2.set_yticks(range(0, 25, 2))
    ax2.set_ylabel("Wind Speed [mph], blue dots")
    ax2.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%-I %p\n%-d %b'))
    ax.axvspan(
        datetime.datetime(2019, 1, 29, 17), datetime.datetime(2019, 1, 31, 12),
        zorder=-1, color='tan')
    ax.text(
        datetime.datetime(2019, 1, 30, 14), -55, "%s CLOSED!" % (school, ),
        bbox=dict(color=conf[school][0]), ha='center', va='center',
        color=conf[school][1], fontsize=18
    )
    fig.savefig('%s.png' % (school, ))


if __name__ == '__main__':
    main(sys.argv)
