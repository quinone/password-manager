from flask import g, session
import pytest
from app.db import get_db


def test_register(client, app):
    assert client.get("auth/register").status_code == 200
    response = client.post(
        "/auth/register",
        data={
            "email_address": "a@a.com",
            "password": "1StrongPassword!",
            "retype_password":"1StrongPassword!",
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

valid_password = "Testpassword1!"
valid_email = "test@test.com"
valid_name = "Test Name"
valid_hint = "Test Hint"

'''
@pytest.mark.parametrize(
    ("email", "password","retype_password", "name", "password_hint", "message"),
    (
        ("", valid_password, valid_password, valid_name,valid_hint, b"Email address is required."),
        (valid_email, "", valid_password, valid_name, valid_hint, b"Password is required."),
        (valid_email, valid_password, "", valid_name, valid_hint, b"Passwords do not match."),
        (valid_email, valid_password,valid_password, "",valid_hint, b"Name is required."),
        (valid_email, valid_password, valid_password, valid_name, "", b"Password hint is required."),
    ),
)

def test_register_validate_input(client, email, password, retype_password, name, password_hint, message):
    response = client.post(
        "/auth/register",
        data={"email_address": email, "password": password,"retype_password": retype_password, "name": name, "hint": password_hint},
    )
    assert message in response.data
'''

def test_login(client, auth):
    assert client.get("/auth/login").status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/vault/profile"

    with client:
        response = client.get("/vault/profile")
        db = get_db()
        assert session["user_id"] == 1
        assert g.user['name'] == 'test'


@pytest.mark.parametrize(
    ("email", "password", "message"),
    (
        ("a", "test", b"Invalid email or password. Please try again."),
        ("test", "a", b"Invalid email or password. Please try again."),
    ),
)
def test_login_validate_input(auth, email, password, message):
    response = auth.login(email, password)
    assert message in response.data
