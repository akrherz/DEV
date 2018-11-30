"""Query our version.jsp to see what it returns."""
import requests


def main():
    """Go Main Go."""
    payload = "<available></available>"
    # base = "http://openfire:8080/ignite/"
    base = "http://www.igniterealtime.org/"
    req = requests.post(base + "projects/openfire/versions.jsp",
                        dict(type='available', query=payload))
    if len(req.content) < 1800:
        print(req.content)


if __name__ == '__main__':
    main()
