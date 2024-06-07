from flask import session
import pytest


valid_route="/vault/Passing Folder"
@pytest.mark.parametrize(
        "result",
        [
            (b"Fake Name"),
            (b"Fake Username"),
            (b"asdf1234"),
            (b"www.google.com"),
            (b"note"),
        ],
        ids=[
            "Correct name",
            "correct username",
            "Correct password",
            "Correct uri",
            "Correct note"
        ]
)

def test_folder_route(client, auth, result):
    # Simulate a login
    response = auth.login()
    with client:
        response = client.get("/vault/Passing Folder")
        assert response.status_code == 200
        assert result in response.data


def test_access_other_users_folder(client, auth):
    auth.login()
    with client:
        response = client.get("/vault/Other users Folder", follow_redirects=True)
        # Print response to help debug
        print("Post response status code:", response.status_code)
        print("Post response headers:", response.headers)
        print("Post response data:", response.data)
        assert response.status_code == 200
        assert response.request.path == "/vault/"


def test_create_new_folder_path(auth, client):
    pass
    # Set session variable using session transaction
    #with client.session_transaction() as sess:
    #    sess['user_ID'] = 1
    #    print(session.get('user_ID'))
    #    # Access the new folder page
    #    response = client.get("/vault/new-folder")
    #    print("New folder page response status code:", response.status_code)
    #    assert response.status_code == 200
#

def test_create_new_folder(auth, client):
    response = auth.login()
    with client:
        # Check if login was successful
        print("Login response status code:", response.status_code)
        assert response.status_code == 302

        # Access the new folder page
        response = client.get("/vault/new-folder")
        print("New item page response status code:", response.status_code)
        assert response.status_code == 200
        response = client.post(
            "/vault/new-folder",
            data = {
                "folder_name":"New",
            },
            follow_redirects=True,
        )
        print("Post response status code:", response.status_code)
        print("Post response headers:", response.headers)
        print("Post response data:", response.data)
        # Test redirection to vault
        assert response.request.path == "/vault/"
        # Test for successful message
        assert b"Folder added successfully." in response.data


def test_create_duplicate_folder_same_user():
    pass


def test_create_duplicate_folder_other_user():
    pass

