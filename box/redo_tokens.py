"""Sometimes, my stored tokens get fouled up, fix this"""
from boxsdk import Client, OAuth2
from pyiem.util import get_properties, set_property


def _store_tokens(access_token, refresh_token):
    """Callback if we needed to have our tokens refreshed"""
    print("store_tokens called")
    print("access_token %s" % (access_token, ))
    print("refresh_token %s" % (refresh_token, ))
    set_property('boxclient.access_token', access_token)
    set_property('boxclient.refresh_token', refresh_token)


def main():
    """Go Main Go"""
    iemprops = get_properties()
    oauth = OAuth2(
        client_id=iemprops['boxclient.client_id'],
        client_secret=iemprops['boxclient.client_secret'],
        store_tokens=_store_tokens
    )
    print(oauth.get_authorization_url('https://mesonet.agron.iastate.edu'))
    oauth.authenticate(input("What was the code? "))
    client = Client(oauth)
    print(client.user(user_id='me').get())


if __name__ == '__main__':
    main()
