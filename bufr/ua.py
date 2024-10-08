import json

from pybufrkit.decoder import Decoder
from pybufrkit.renderer import NestedJsonRenderer


# Add a simple JSON serializer for bytes
class MyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return o.decode("utf-8")
        return super().default(o)


decoder = Decoder()
with open("IU_2024100813.bufr", "rb") as ins:
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
    obs = {"pres": None, "tmpk": None, "dwpk": None, "height": None}
    for msg in msgs:
        if msg["id"] == "004086":
            print(obs["pres"], obs["height"], obs["tmpk"], obs["dwpk"])
            continue
        if msg["id"] == "010009":
            obs["height"] = msg["value"]
            continue
        if msg["id"] == "007004":
            obs["pres"] = msg["value"]
            continue
        if msg["id"] == "012101":
            obs["tmpk"] = msg["value"]
            continue
        if msg["id"] == "012103":
            obs["dwpk"] = msg["value"]
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
