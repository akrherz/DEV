"""markup the markdown"""

JIRA = "https://igniterealtime.atlassian.net/browse/"


for line in open("changelog"):
    if line.startswith("###"):
        print("<h3>%s</h3>" % line[3:].strip())
        print("<ul>")
        continue
    if line.strip() == "":
        continue
    issue, rest = line.split(maxsplit=1)
    print(
        f'    <li>[<a href="{JIRA}{issue}">{issue}</a>] - {rest.strip()}</li>'
    )
