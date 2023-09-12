from urllib.parse import quote_plus, urlencode
from flask import Blueprint, current_app, redirect, session, url_for
from authlib.integrations.flask_client import OAuth

from config import config

auth_bp = Blueprint('auth', __name__)

auth0_config = config['AUTH0']
oauth = OAuth(current_app)

domain = auth0_config["DOMAIN"]
client_id = auth0_config["CLIENT_ID"]
client_secret = auth0_config["CLIENT_SECRET"]

oauth.register(
    "auth0",
    client_id=client_id,
    client_secret=client_secret,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{domain}/.well-known/openid-configuration'
)


@auth_bp.route("/test")
def test():
    return session.get("user").get("userinfo").get("sub")

@auth_bp.route("/login")
def login():
    """
    Redirects the user to the Auth0 Universal Login (https://auth0.com/docs/authenticate/login/auth0-universal-login)
    """
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True)
    )

@auth_bp.route("/signup")
def signup():
    """
    Redirects the user to the Auth0 Universal Login (https://auth0.com/docs/authenticate/login/auth0-universal-login)
    """
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True),
        screen_hint="signup"
    )


@auth_bp.route("/logout")
def logout():
    """
    Logs the user out of the session and from the Auth0 tenant
    """
    session.clear()
    return redirect(
        "https://" + domain
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("notes.index", _external=True),
                "client_id": client_id,
            },
            quote_via=quote_plus,
        )
    )

@auth_bp.route("/callback", methods=["GET", "POST"])
def callback():
    """
    Callback redirect from Auth0
    """
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")