from flask import g, session
import pytest
from app.db import get_db

def test_new_item(client, auth, app):
     ## Simulate a login
    response = auth.login()
    with client:
        assert client.get("/vault/new-item").status_code == 200
        # Ensure the user_id is set in the session
        assert session.get("user_id") == 1
        # post with values in each field
        response = client.post(
            "/vault/new-item",
            data={
                "name": "Sample",
                "username": "Example1",
                "password": "weakpassword",
                "uri": "www.google.com",
                "notes": "My sample google account info", 
                #"folderID", 
            },
        )
        #test redirection to vault
        assert response.headers["Location"] == "/vault"
        #test for Successful message
        assert b"Successfully submitted new item" in response.data 
        #test for entry in database
        with app.app_context():
            assert (
                get_db()
                .execute(
                    "SELECT * FROM ITEM WHERE NAME = 'Sample'",
                )
                .fetchone()
                is not None
            )



