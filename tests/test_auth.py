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
            "retype_password": "1StrongPassword!",
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


"""@pytest.mark.parametrize(
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
    assert message in response.data"""


def test_login(client, auth):
    assert client.get("/auth/login").status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/vault/profile"

    with client:
        response = client.get("/vault/profile")
        db = get_db()
        assert session["user_id"] == 1
        assert g.user["name"] == "test"


@pytest.mark.parametrize(
    ("email", "password", "message"),
    (
        ("a", "test", b"Invalid email or password. Please try again."),
        ("test", "a", b"Invalid email or password. Please try again."),
        (valid_email, "a", b"Invalid email or password. Please try again."),
    ),
)
def test_login_validate_input(auth, email, password, message):
    response = auth.login(email, password)
    assert message in response.data


def test_logout(client, auth):
    ## Simulate a login
    response = auth.login()
    with client:
        response = client.get("/vault/profile")
        assert session["user_id"] == 1
        ## Ensure the user_id is set in the session
        assert session.get("user_id") == 1
        ## Perform the logout
        response = client.get("/auth/logout", follow_redirects=True)
        # assert response.headers['Location'] == "/auth/login"
        assert "user_id" not in session
        assert b"You have been logged out." in response.data


# As new routes are created they can be added here
@pytest.mark.parametrize(
    "test_path",
    [
        ("/vault/"),
        ("/vault/profile"),
        ("/vault/new-item"),
        ("/vault/new-folder"),
    ],
    ids=["Check vault", "check profile", "check new-item", "check new-folder"],
)
def test_unauthenticated_route_access(client, test_path):
    """This test should redirect to /auth/login"""

    response = client.get(test_path, follow_redirects=True)
    # Print response to help debug
    print("Post response status code:", response.status_code)
    print("Post response headers:", response.headers)
    print("Post response data:", response.data)
    # Status code for redirect should be 200 after redirect
    assert response.status_code == 200
    # Flash message of 'You are not logged in.'
    assert b"You are not logged in." in response.data
    assert response.request.path == "/auth/login"


# As new routes are created they can be added here
@pytest.mark.parametrize(
    "test_path_logout_required",
    [
        ("/auth/login"),
        ("/auth/register"),
    ],
    ids=["Check login", "check register"],
)

# Test logout_required decorator
def test_logout_required(auth, client, test_path_logout_required):
    with client:
        ## Simulate a login
        auth.login()
        # Ensure the user_id is set in the session
        assert session.get("user_id") == 1
        # Go to test paths
        response = client.get(test_path_logout_required, follow_redirects=True)
        # Print response to help debug
        print("Post response status code:", response.status_code)
        print("Post response headers:", response.headers)
        print("Post response data:", response.data)
        assert b"You are already authenticated." in response.data
        assert response.request.path == "/vault/profile"
