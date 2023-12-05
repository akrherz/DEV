import json

from pybufrkit.decoder import Decoder
from pybufrkit.renderer import NestedJsonRenderer

from pyiem.util import convert_value


# Add a simple JSON serializer for bytes
class MyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return o.decode("utf-8")
        return super().default(o)


decoder = Decoder()
with open("bufr2", "rb") as ins:
    bufr_message = decoder.process(ins.read())

DIRECTS = {
    "004001": "year",
    "004002": "month",
    "004003": "day",
    "004004": "hour",
    "004005": "minute",
    "001015": "station_name",
    "007030": "elevation",
    "005001": "lat",
    "006001": "lon",
}


def glean_data(msgs):
    """see what we can do with this."""
    data = {}
    displacement = 0
    for msg in msgs:
        print(msg["id"], msg["description"], msg["value"])
        if msg["id"].startswith("001"):
            data[msg["id"]] = msg["value"]
            continue
        if msg["id"] == "004024":  # TIME PERIOD OR DISPLACEMENT
            displacement = msg["value"]
            continue
        if msg["id"] in DIRECTS:
            data[DIRECTS[msg["id"]]] = msg["value"]
            continue
        if msg["id"] == "010004":
            data["pres"] = msg["value"] / 100.0
            continue
        if msg["id"] == "010051":
            data["mslp"] = msg["value"] / 100.0
            continue
        if msg["id"] == "012101":
            data["tmpf"] = convert_value(msg["value"], "degK", "degF")
            continue
        if msg["id"] == "012103":
            data["dwpf"] = convert_value(msg["value"], "degK", "degF")
            continue
        if msg["id"] == "013003":
            data["relh"] = msg["value"]
            continue
        if msg["id"] == "020001":
            data["vsby"] = convert_value(msg["value"], "m", "mile")
            continue
        if msg["id"] == "011002" and displacement >= -10:
            data["sknt"] = convert_value(
                msg["value"], "meter per second", "knot"
            )
            continue
        if msg["id"] == "011001" and displacement >= -10:
            data["drct"] = msg["value"]
            continue
        if msg["id"] == "011041" and displacement >= -10:
            data["gust"] = convert_value(
                msg["value"], "meter per second", "knot"
            )
            continue
        if msg["id"] == "011043" and displacement >= -10:
            data["gust_drct"] = msg["value"]
            continue
    # Attempt to compute a station ID
    if "001125" in data:
        data["sid"] = (
            f"{data['001125']}-"
            f"{data['001126']}-"
            f"{data['001127']}-"
            f"{data['001128'].decode('ascii').strip()}"
        )
    if "001002" in data:
        data["sid"] = f"0-TBDFROMHEADER-0-{data['001002']}"
    if "001015" in data:
        data["sname"] = data["001015"].decode("ascii").strip()
    return data


def render_members(members, msgs):
    """recursive."""
    for member in members:
        if isinstance(member, list):
            render_members(member, msgs)
        elif isinstance(member, dict):
            if "factor" in member:
                # print("FACTOR:", member["factor"])
                msgs.append(member["factor"])
            if "value" in member:
                if member["value"] is not None:
                    # print(member)
                    msgs.append(member)
            elif "members" in member:
                render_members(member["members"], msgs)
            else:
                print("Dead end", member)
        else:
            # print(member)
            msgs.append(member)


jdata = NestedJsonRenderer().render(bufr_message)
for section in jdata:
    for parameter in section:
        if isinstance(parameter["value"], list):
            print("-->", parameter["name"], type(parameter["value"]))
            for entry in parameter["value"]:
                print("----> entry")
                if isinstance(entry, list):
                    msgs = []
                    render_members(entry, msgs)
                    print(glean_data(msgs))
                else:
                    # unexpanded_descriptors
                    print(entry)
        else:
            print("-->", parameter["name"], parameter["value"])
