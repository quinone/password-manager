from flask import g, session
import pytest
from app.db import get_db

def test_new_item(client, auth, app):
    # Simulate a login
    response = auth.login()
    with client:
        # Check if login was successful
        print("Login response status code:", response.status_code)
        assert response.status_code == 302

        # Access the new item page
        response = client.get("/vault/new-item")
        print("New item page response status code:", response.status_code)
        assert response.status_code == 200

        # Ensure the user_id is set in the session
        with client.session_transaction() as session:
            user_id = session.get("user_id")
            print("Session user_id:", user_id)
            assert user_id == 1

        # Post with values in each field
        response = client.post(
            "/vault/new-item",
            data={
                "name": "Sample",
                "username": "Example1",
                "password": "weakpassword",
                "uri": "www.google.com",
                "notes": "My sample google account info",
                "folderID": 1,  # Add a value for folderID
            },
            follow_redirects=True
        )
        print("Post response status code:", response.status_code)
        print("Post response headers:", response.headers)
        print("Post response data:", response.data)

        # Test redirection to vault
        assert response.request.path == "/vault/"
        
        # Test for successful message
        assert b"Successfully submitted new item" in response.data


def test_unauthenticated_vault_access(client):
    ''' This test should redirect to /auth/login '''

    response = client.get("/vault", follow_redirects=True)
    # Print response to help debug
    print("Post response status code:", response.status_code)
    print("Post response headers:", response.headers)
    print("Post response data:", response.data)
    # Status code for redirect should be 200 after redirect
    assert response.status_code == 200
    # Flash message of 'You are not logged in.'
    assert b'You are not logged in.' in response.data
    assert response.request.path == '/auth/login'


def test_authenticated_vault_view_users_items():
    ''' This test should check if the items are shown for the users items'''
    pass


def test_authenticated_vault_view_others_items():
    ''' This test should attempt to access other users items and fail'''
    pass