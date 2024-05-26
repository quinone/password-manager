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
g