from cryptography.fernet import Fernet
import pytest

from app.db import get_db
from app.db_cryptography import (
    decrypt_item,
    get_cipher,
    encrypt_data,
    decrypt_data,
    insert_encrypted_item,
)


TEST_ENCRYPTION_KEY = b"GIOMjevPEyxq7DfrQnYFDGi0hJ9GurcOAq0c_H09iEE="
TEST_DATA = "This string is to be encrypted"


def test_encrypt_data(app):
    with app.app_context():
        encrypted_data = encrypt_data(TEST_DATA)
        decrypted_data = decrypt_data(encrypted_data)
        assert decrypted_data == TEST_DATA
        # encrypted data should be different every time
        assert encrypt_data(TEST_DATA) != encrypted_data


def test_decrypt_data(app):
    with app.app_context():
        decrypted_data = decrypt_data(
            b"gAAAAABmVOgZwKvhTzxiy7qEI6uD0pZ4lGGZvN3-YtZ4D6kOuQVijXEFBnF-244BgCR9RbDiW3j_grwG28R0UknsDc6PMJ0F-iiZoOMr0p_yY5p95vji6Wg="
        )
        assert decrypted_data == TEST_DATA


def test_insert_encrypted_item(app):
    with app.app_context():
        insert_encrypted_item(
            userID="2",
            name="New item",
            username="New user",
            password="SuperPassword",
            uri="www.example.com",
            notes="top secret notes",
            folder_ID=1,
        )

        # check if the item is correctly inserted
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM ITEM WHERE ID = 2")
        item = cursor.fetchone()
        print(f"Item from database: {item}")
        assert item is not None

        decrypted_item = decrypt_item(2)
        print(f"Decrypted item: {decrypted_item}")
        assert decrypted_item is not None

        assert decrypted_item.get("userID") == 2
        assert decrypted_item.get("name") == "New item"
        assert decrypted_item.get("username") == "New user"
        assert decrypted_item.get("password") == "SuperPassword"
        assert decrypted_item.get("uri") == "www.example.com"
        assert decrypted_item.get("notes") == "top secret notes"


def test_decrypt_item(app):
    with app.app_context():
        # check if the item is correctly inserted
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM ITEM WHERE ID = 1")
        item = cursor.fetchone()
        print(f"Item from database: {item}")
        assert item is not None

        decrypted_item = decrypt_item(1)
        print(f"Decrypted item: {decrypted_item}")
        assert decrypted_item is not None

        assert decrypted_item.get("userID") == 1
        assert decrypted_item.get("name") == "Fake Name"
        assert decrypted_item.get("username") == "Fake Username"
        assert decrypted_item.get("password") == "asdf1234"
        assert decrypted_item.get("uri") == "www.google.com"
        assert decrypted_item.get("notes") == "note"
