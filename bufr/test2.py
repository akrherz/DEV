"""Explore."""

import json

import pandas as pd
from pybufrkit.decoder import Decoder
from pybufrkit.renderer import NestedJsonRenderer
from pyiem.util import convert_value, logger

LOG = logger()

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


# Add a simple JSON serializer for bytes
class MyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return o.decode("utf-8")
        return super().default(o)


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


def walk(entry, node, result):
    """Recursive walk."""
    if isinstance(entry, list):
        all_values = all("value" in x for x in entry)
        if all_values:
            leaf = {x["id"]: x["value"] for x in entry}
            result.setdefault(node, []).append(leaf)
            return
        for subentry in entry:
            walk(subentry, node, result)
        return
    node = f"{node}/{entry['id']}"
    if "value" in entry:
        result.setdefault(node, []).append({entry["id"]: entry["value"]})
        return
    if "members" in entry:
        all_values = all("value" in x for x in entry["members"])
        if all_values:
            leaf = {x["id"]: x["value"] for x in entry["members"]}
            result.setdefault(node, []).append(leaf)
            return
        for member in entry["members"]:
            walk(member, node, result)

    # Dead end


def process_payload(payload):
    """Do something with this payload."""
    decoder = Decoder()
    bufr_message = decoder.process(payload)
    sections = NestedJsonRenderer().render(bufr_message)
    # Require 5 sections, which seems to be the norm
    if len(sections) != 5:
        LOG.info("Invalid number of sections: %s", len(sections))
        return
    # section 0 is the BUFR header, which denotes length and edition
    # section 2 is usually skipped
    # section 3 is descriptors
    section3 = {x["name"]: x["value"] for x in sections[2]}
    n_subsets = section3["n_subsets"]
    print("------ n_subsets", n_subsets)
    # section 4 is the data
    section4 = {x["name"]: x["value"] for x in sections[3]}
    for subset in range(n_subsets):
        print(f"------ Subset {subset}")
        result = {}
        for entry in section4["template_data"][subset]:
            walk(entry, "", result)
        for key, res in result.items():
            print(key, res[:20])
        df = pd.DataFrame(result["/309052/101000/303054"])
        print(df)


def read_in_chunks(file_object, chunk_size=1024):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def process_file(file_path):
    with open(file_path, "rb") as ins:
        buffer = b""
        for chunk in read_in_chunks(ins):
            buffer += chunk
            while b"BUFR" in buffer:
                payload, buffer = buffer.split(b"BUFR", 1)
                yield payload
    yield buffer


def main():
    """Go Main Go."""
    for i, payload in enumerate(process_file("IU_2024100813.bufr")):
        if i == 0:
            continue
        process_payload(b"BUFR" + payload)


if __name__ == "__main__":
    main()
