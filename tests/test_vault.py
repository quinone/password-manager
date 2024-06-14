from flask import g, session
import pytest
from app.db import get_db


@pytest.mark.parametrize(
    ("route", "message"),
    (
        ("/vault/new-item", b"Successfully submitted new item"),
        ("/vault/edit-item/1", b"Successfully updated the item"),
    ),
    ids=[
        "Test new-item",
        "Test edit-item",
    ],
)
def test_item(client, auth, route, message):
    # Simulate a login
    response = auth.login()
    with client:
        # Check if login was successful
        print("Login response status code:", response.status_code)
        assert response.status_code == 302

        # Access the new item page
        response = client.get(route)
        print("New item page response status code:", response.status_code)
        assert response.status_code == 200

        # Ensure the user_id is set in the session
        with client.session_transaction() as session:
            user_id = session.get("user_id")
            print("Session user_id:", user_id)
            assert user_id == 1  # 1

        # Post with values in each field
        response = client.post(
            route,
            data={
                "name": "Sample",
                "username": "Example1",
                "password": "weakpassword",
                "uri": "www.google.com",
                "notes": "My sample google account info",
                "folder_select": 1,  # Add a value for folderID
            },
            follow_redirects=True,
        )
        print("Post response status code:", response.status_code)
        print("Post response headers:", response.headers)
        print("Post response data:", response.data)

        # Test redirection to vault
        assert response.request.path == "/vault/"

        # Test for successful message
        assert message in response.data


# As new routes are created they can be added here
@pytest.mark.parametrize(
    "test_path",
    [
        ("/vault/"),
        ("/vault/profile"),
        ("/vault/new-item"),
        ("/vault/new-folder"),
        ("/vault/folder/Example Folder"),
        ("/vault/generate-password"),
        ("/vault/edit-item/1"),
    ],
    ids=[
        "Check vault",
        "check profile",
        "check new-item",
        "check new-folder",
        "check example folder",
        "Check generate-password",
        "Check edit-item/",
    ],
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
    "test_path",
    [
        ("/vault/"),
        ("/vault/profile"),
        ("/vault/new-item"),
        ("/vault/new-folder"),
        ("/vault/folder/Example Folder"),
        ("/vault/generate-password"),
        ("/vault/edit-item/1"),
    ],
    ids=[
        "Check vault",
        "check profile",
        "check new-item",
        "check new-folder",
        "check example folder",
        "Check generate-password",
        "Check edit-item/",
    ],
)
def test_authenticated_route_access(client, auth, test_path):
    """Test should load path."""
    with client:
        auth.login()
        response = client.get(test_path)
        print("Response status_code: ", response.status_code)
        assert response.status_code == 200


def test_authenticated_vault_view_users_items(client, auth):
    """This test should check if the items are shown for the users items"""
    pass

    """# Simulate a login
    response = auth.login()
    with client:
        # Check if login was successful
        print("Login response status code:", response.status_code)
        assert response.status_code == 302

        # Access the new item page
        response = client.get("/vault/")
        print("Vault page response status code:", response.status_code)
        assert response.status_code == 200

        # Ensure the user_id is set in the session
        with client.session_transaction() as session:
            user_id = session.get("user_id")
            print("Session user_id:", user_id)
            assert user_id == 1

        # Check for rendering of test items
        assert b'test' in response.data 
        for item in ['1',
        '1',
        'Fake Name',
        'Fake Username',
        'asdf1234',
        'www.google.com',
        'note' ]:
            assert item.encode('utf-8') in response.data
        # Print response to help debug
        print("Post response status code:", response.status_code)
        print("Post response headers:", response.headers)
        print("Post response data:", response.data)"""


def test_authenticated_vault_view_others_items():
    """This test should attempt to access other users items and fail"""
    pass


def test_search(client, auth):
    # login
    auth.login()
    response = client.get("/vault/")
    assert b"Search" in response.data
    # Post with values in each field
    response = client.post(
        "/vault/search",
        data={"searched": "Fake Name"},
        follow_redirects=True,
    )
    print("Post response status code:", response.status_code)
    print("Post response headers:", response.headers)
    print("Post response data:", response.data)
    assert b"asdf1234" in response.data
    assert b"www.google.com" in response.data
    assert b"note" in response.data
