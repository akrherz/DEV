"""Eh."""

import re

import click

INFORE = re.compile("'id': '(\d+)', 'description': '(.*)', 'value'")


@click.command()
@click.argument("log_file", type=click.File("r"))
def main(log_file):
    """Go."""
    hits = {}
    for line in log_file:
        m = INFORE.search(line)
        if m:
            key = f"{m.group(1)} {m.group(2)}"
            hits[key] = hits.get(key, 0) + 1
    for key in sorted(hits, key=hits.get, reverse=True):
        print(f"{hits[key]:4} {key}")


if __name__ == "__main__":
    main()
