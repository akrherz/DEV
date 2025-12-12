"""markup the markdown.

Generate from Jira with MD and `Issue Key` linked not-set.
"""

JIRA = "https://igniterealtime.atlassian.net/browse/"


def main():
    """Go Main."""
    with open("changelog", encoding="utf-8") as fh:
        for line in fh:
            if line.strip() == "":
                continue
            # The line is basically markdown, which ends up escaping mundane
            # things ok in HTML, like `_`.  So we remove any backslashes
            line = line.replace("\\", "")
            if line.startswith("### "):
                print(f"</ul>\n\n<h2>{line[3:].strip()}</h2>")
                print("<ul>")
                continue
            issue, rest = line.split(maxsplit=1)
            print(
                f'    <li>[<a href="{JIRA}{issue}">{issue}</a>] - '
                f"{rest.strip()}</li>"
            )
    print("</ul>")


if __name__ == "__main__":
    main()
