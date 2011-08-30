import oauth2 as oauth
import urllib2
import base64
from urllib import urlencode

BASE_SITE_URL = "http://localhost:8000/"
ROOT_API_URL = BASE_SITE_URL + "api/1.0/"
OAUTH_CONSUMER_KEY = "451cffaa88bd49e881068349b093598a"
OAUTH_SECRET_KEY = "j5rdVtVhKu4VfykM"
USER_LOGIN = "benoit.woj@gmail.com"
USER_PASSWORD = "ben"

def get_client():
    consumer = oauth.Consumer(key=OAUTH_CONSUMER_KEY, secret=OAUTH_SECRET_KEY)
    client = oauth.Client(consumer)
    return consumer, client

def make_connection():
    """
    Demo Oauth connection function
    """
    from urllib import urlencode
    import urlparse

    consumer, client = get_client()

    def request(url, *args, **kwargs):
        return client.request(BASE_SITE_URL + url, *args, **kwargs)

    response, csrf_token = request("login_headless/")

    headers = {'Cookie':response['set-cookie']}
    login_body = urlencode({
        "password":USER_PASSWORD,
        "email":USER_LOGIN,
        "exists":1,
        "csrfmiddlewaretoken": csrf_token
    })

    response, content = request("login_headless/", "POST", login_body, headers)
    headers = {'Cookie':response['set-cookie']}


    response, content = request("oauth/request_token/?oauth_callback=oob", "GET")
    request_token = dict(urlparse.parse_qsl(content))

    get_token_body = urlencode({
        "oauth_token": request_token["oauth_token"],
    })

    response, csrf_token = request("oauth/authorize/?"+get_token_body, "GET", headers=headers)
    headers = {'Cookie':response['set-cookie']}

    post_token_body = urlencode({
        "csrfmiddlewaretoken": csrf_token,
        "oauth_token": request_token["oauth_token"],
        "authorize_access": True,
    })

    response, verifier = request("oauth/authorize/", "POST", post_token_body, headers=headers)

    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(verifier)
    client = oauth.Client(consumer, token)

    response, content = request("oauth/access_token/", "POST")

    access_token = dict(urlparse.parse_qsl(content))
    token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])

    client = oauth.Client(consumer, token)

    return client