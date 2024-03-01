"""Review our dependencies."""

import glob
import json
import os


def main():
    """Go Main Go."""
    os.chdir("/opt/miniconda3/envs/prod/conda-meta")
    deps = {}
    for fn in glob.glob("*.json"):
        with open(fn, encoding="utf8") as fp:
            js = json.load(fp)
        for dep in js["depends"]:
            if dep.find("<") == -1:
                continue
            key = f"{fn} -> {dep}"
            pack = dep.split()[0]
            entry = deps.setdefault(pack, {})
            item = entry.setdefault(dep, {"items": []})
            item["items"].append(key)
    keys = list(deps.keys())
    keys.sort()
    for pack in keys:
        for entry in deps[pack]:
            print(f"{pack} -> {entry}")
            for item in deps[pack][entry]["items"]:
                print(f"    {item}")


if __name__ == "__main__":
    main()
