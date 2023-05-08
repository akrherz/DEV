"""
Receive bot messages and write to our hackish queue.
"""
import json
import os

from twisted.internet import reactor
from twisted.web import resource, server

from pyiem.util import get_properties, utc


class RootResource(resource.Resource):
    """Our web protocol."""

    def isLeaf(self):
        """allow uri"""
        return True

    def __init__(self, secret):
        """Constructor"""
        resource.Resource.__init__(self)
        self.secret = secret

    def render_POST(self, request):
        """Service the request."""
        payload = json.loads(request.content.read())
        # Cough verify secret
        if payload.get("secret") != self.secret:
            return b"Unauthorized"
        payload.pop("secret")
        screen_name = payload.get("screen_name")
        mydir = f"botdata/{screen_name}"
        if not os.path.isdir(mydir):
            return b"Invalid screen_name"
        with open(
            f"{mydir}/tweet_{utc():%Y%m%dT%H%M%S.%f}.json",
            "w",
            encoding="utf-8",
        ) as fp:
            json.dump(payload, fp)

        return b"ACK"


def main():
    """Go Main Go."""
    proto = server.Site(RootResource(get_properties()["iembot2secret"]))
    reactor.listenTCP(10101, proto)
    reactor.run()


if __name__ == "__main__":
    main()
