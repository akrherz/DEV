"""Specialized WEPS worker that simply copies files for others to use."""

import shutil
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from functools import partial
from pathlib import Path

import click
import requests
from dailyerosion.workflows.wepsrun import WEPSJobPayload
from dailyerosion.workflows.worker import consume_queue
from pika.channel import Channel
from pydantic import ValidationError
from pyiem.util import logger

DAY1 = date(2007, 1, 1)
LOG = logger()
MEMORY = {
    "runs": 0,
    "timestamp": time.time(),
}


def generate_runfile(
    lon: float,
    lat: float,
    clifile: str,
    windfile: str,
    manfile: str,
    ifcfile: str,
    rectangle_length_m: float,
    rectangle_width_m: float,
    rectangle_rotation_deg: float,
) -> str:
    """Create the run file settings."""
    return f"""
#VERSION=1.05
#------------ WEPS SIMULATION RUN FILE ------------
# Note: Lines beginning with '#' are comment lines.
#       Lines beginning with '#   RFD' are comments used by the interface.
#
# --USER INFORMATION
#   RFD-UserName
Exercise 1
#   FarmId TractId FieldId runtypedisp RotationYears CycleCount
 |  |  | Date | 20 | 1
#   RFD-Site
FIPS:US-WI-097
#
# --SITE INFORMATION
#   Signed Latitude
+{lat}
#   Signed Longitude
{lon}
#   RFD-Elevation(meters)
337.99272
#   RFD-ClimateFlag|RFD-cligen.station
test1
#   RFD-WindFlag|RFD-windgen.station
test2
#
# --SIMULATION PERIOD
#   RFD-StartDate(day month year)
01 01 2007
#   RFD-EndDate(day month year)
31 12 2026
#   RFD-TimeSteps(per day)
24
#
# --RUN FILE FILENAMES (INPUT)
#   RFD-climate file
{clifile}
#   RFD-wind file
{windfile}
#   RFD-sub-daily file
none
#   RFD-SoilFile
{ifcfile}
#   RFD-ManageFile
{manfile}
#
# --WEPS OUTPUT OPTIONS
#   RFD-OutputFile
null
#   RFD-ReportForm
0 0 0 0 0 0
#   RFD-OutputPeriod
2
#   RFD-SubmodelOutput
0 1 0 0 0 0
#   RFD-DebugOutput
0 0 0 0 0 0
#
# --SIMULATION REGION INFORMATION
#   RFD-RegionAngle(degrees clockwise from North)
{rectangle_rotation_deg}
#   Origin coordinates of simulation region (meters)
0.0  0.0
#    RFD-XLength(meters)  RFD-YLength(meters)
{rectangle_length_m}  {rectangle_width_m}
#   RFD-Scales(place holder line - needed for older versions of WEPS)
5.5 5.5
#
#   RFD-AccNo
1
#   Accounting region coordinates (meters)
0.0  0.0
{rectangle_length_m}  {rectangle_width_m}
#
#   RFD-SubregionNo
1
#   Subregion region coordinates (meters)
0.0  0.0
{rectangle_length_m}  {rectangle_width_m}
#   RFD-AverageSlope(ratio m/m)
-1
#   RFD-BarrierNo
0
0.0 0.0
0.0 0.0
none
0.0
0.0
0.0
#
# --CIRCULAR FIELD INFORMATION
# Note: These fields are not used by the weps simulation.
#       The shape and radius values are used by the user
#       interface to approximate a rectangular field.  They
#       are included here so the reports can display the
#       correct field shape.
#
#   RFD-Shape
circle
#   RFD-Radius
402.87
#   RFD-WaterErosionLoss
0.00
#   RFD-SoilRockFragments
-1
#---------- END OF SIMULATION RUN FILE ------------
"""


def run_weps(payload: WEPSJobPayload) -> None:
    """Actually run WEPS, really.

    Parameters
    ----------
    payload : WEPSJobPayload
        Validated SWEEP job payload containing runfile content and executable.
    """
    basedir = Path("/i/0/weps_all") / payload.huc_12
    basedir.mkdir(parents=True, exist_ok=True)
    basefn = f"{payload.huc_12}_{payload.fpath}"
    # DEP climate files no worky, so we ask the webservice to convert it
    url = (
        "https://mesonet-dep.agron.iastate.edu/dl/climatefile.py?"
        f"lat={payload.lat}&lon={payload.lon}&format=weps"
    )
    resp = requests.get(url, timeout=120)
    with open(basedir / f"{basefn}.cli", "wb") as fh:
        fh.write(resp.content)
    shutil.copyfile(payload.windfile, basedir / f"{basefn}.wnd")
    shutil.copyfile(payload.manfile, basedir / f"{basefn}.man")
    shutil.copyfile(payload.ifcfile, basedir / f"{basefn}.ifc")
    runfile = generate_runfile(
        payload.lon,
        payload.lat,
        f"{basefn}.cli",
        f"{basefn}.wnd",
        f"{basefn}.man",
        f"{basefn}.ifc",
        payload.rectangle_length_m,
        payload.rectangle_width_m,
        payload.rectangle_rotation_deg,
    )
    with open(basedir / f"{basefn}.run", "w") as fh:
        fh.write(runfile)


def run(ch: Channel, delivery_tag, payload):
    """Actually run wepp for this event.

    Parameters
    ----------
    ch : pika.channel.Channel
        The RabbitMQ channel.
    delivery_tag : int
        The message delivery tag for acknowledgment.
    payload : bytes
        The raw message payload from RabbitMQ.
    """
    # We should be fully within a thread at this point...
    try:
        # Parse and validate the payload using Pydantic model
        job = WEPSJobPayload.model_validate_json(payload)
        run_weps(job)

    except ValidationError as exp:
        # Invalid payload structure - log the validation errors
        LOG.error("Invalid payload format: %s", exp)
        LOG.error("Raw payload: %s", payload[:200])  # Log first 200 chars
    except Exception as exp:
        LOG.error("run_weps exception: %s", exp)
        LOG.error("Traceback: %s", traceback.format_exc())

    cb = partial(ack_message, ch, delivery_tag)
    ch.connection.add_callback_threadsafe(cb)


def ack_message(ch: Channel, delivery_tag):
    """Note that `ch` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).
    """
    if ch.is_open:
        ch.basic_ack(delivery_tag)
    else:
        # Channel is already closed, so we can't ACK this message;
        # log and/or do something that makes sense for your app in this case.
        pass
    MEMORY["runs"] += 1


def print_timing():
    """Print timing information."""
    while True:
        time.sleep(300)
        runs = MEMORY["runs"]
        dt = time.time() - MEMORY["timestamp"]
        rate = runs / dt
        MEMORY["runs"] = 0
        MEMORY["timestamp"] = time.time()
        if runs == 0:
            continue
        LOG.info("%s runs over %.3fs for %.3f r/s", runs, dt, rate)


@click.command()
@click.option(
    "--queue", required=True, help="Queue name that matches what enqueue did."
)
def main(
    queue: str,
):
    """Go main Go."""
    # Start a thread to print timing every 300 seconds
    threading.Thread(target=print_timing, daemon=True).start()

    while True:
        # Start a threadpool executor that is associated with a rabbitmq
        # connection.  Run until something bad happens, then start again!
        try:
            with ThreadPoolExecutor(max_workers=8) as executor:
                consume_queue(queue, run, executor, 10, LOG)
            LOG.warning("run_consumer exited cleanly, sleeping 30 seconds")
            time.sleep(30)
        except KeyboardInterrupt:
            LOG.critical("Exiting due to keyboard interrupt")
            break
        except Exception as exp:
            LOG.error("Exception %s, sleeping 30", exp)
            traceback.print_exc()
            time.sleep(30)


if __name__ == "__main__":
    main()
