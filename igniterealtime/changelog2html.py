"""markup the markdown.

Generate from Jira with MD and `Issue Key` set.
"""

JIRA = "https://igniterealtime.atlassian.net/browse/"


def main():
    """Go Main."""
    with open("changelog", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("###"):
                print(f"</ul>\n\n<h2>{line[3:].strip()}</h2>")
                print("<ul>")
                continue
            if line.strip() == "":
                continue
            issue, rest = line.split(maxsplit=1)
            print(
                f'    <li>[<a href="{JIRA}{issue}">{issue}</a>] - '
                f"{rest.strip()}</li>"
            )


if __name__ == "__main__":
    main()
