from flask import g, session
import pytest
from app.db import get_db


def test_register(client, app):
    assert client.get("auth/register").status_code == 200
    response = client.post(
        "/auth/register",
        data={
            "email": "a@a.com",
            "password": "1StrongPassword!",
            "name": "a",
            "hint": "One strong password!",
        },
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert (
            get_db()
            .execute(
                "SELECT * FROM USER WHERE EMAIL = 'a@a.com'",
            )
            .fetchone()
            is not None
        )


@pytest.mark.parametrize(
    ("email", "password", "name", "hint", "message"),
    (
        ("", "a", "a", "a", b"Email address is required."),
        ("a", "", "a", "a", b"Password is required."),
        ("a", "a", "", "a", b"Name is required."),
        ("a", "a", "a", "", b"Password hint is required."),
    ),
)
def test_register_validate_input(client, email, password, name, hint, message):
    response = client.post(
        "/auth/register",
        data={"email": email, "password": password, "name": name, "hint": hint},
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get("/auth/login").status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        response = client.get("/")
        assert session.get("user_id") == 1
        assert "test" in g.user


@pytest.mark.parametrize(
    ("email", "password", "message"),
    (
        ("a", "test", b"Incorrect username or password"),
        ("test", "a", b"Incorrect username or password"),
    ),
)
def test_login_validate_input(auth, email, password, message):
    response = auth.login(email, password)
    assert message in response.data
