import os
import tempfile

from pytest import fixture
from app import create_app
from app.db import get_db, init_db


with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf-8")


@fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
        }
    )

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@fixture
def client(app):
    return app.test_client()


@fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client) -> None:
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")
    

@fixture
def auth(client):
    return AuthActions(client)