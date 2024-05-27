import os
import tempfile

import pytest
from app import create_app
from app.db import get_db, init_db


with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
        }
    )
    app.config[
        "ENCRYPTION_KEY"
    ] = "GIOMjevPEyxq7DfrQnYFDGi0hJ9GurcOAq0c_H09iEE="  # "3TirqVc7o7Fk7PzoMwUQCVCWS3ad4C2qArDxWV-Sej8="
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing,

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email="test@test.com", password="testpassword"):
        return self._client.post(
            "/auth/login", data={"email": email, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
