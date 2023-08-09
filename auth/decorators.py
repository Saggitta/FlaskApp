from flask import redirect, session, url_for
from functools import wraps

class AuthError():
    def __init__(self, error, status_code) -> None:
        self.error = error
        self.status_code = status_code

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("user") is None:
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated