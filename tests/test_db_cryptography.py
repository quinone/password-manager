from cryptography.fernet import Fernet
import pytest

from app.db import get_db, query_db
from app.db_cryptography import (
    decrypt_item,
    delete_encrypted_item,
    encrypt_data,
    decrypt_data,
    get_folder_ID,
    get_folder_name,
    insert_encrypted_item,
    update_encrypted_item,
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
    with app.app_context():
        # check if the item is correctly inserted
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM ITEM WHERE NAME = 'New item'")
        item = cursor.fetchone()
        print(f"Item from database: {item}")
        assert item is not None

        decrypted_item = decrypt_item(item[0])
        print(f"Decrypted item: {decrypted_item}")
        assert decrypted_item is not None

        assert decrypted_item.get("USER_ID") == 2
        assert decrypted_item.get("NAME") == "New item"
        assert decrypted_item.get("USERNAME") == "New user"
        assert decrypted_item.get("PASSWORD") == "SuperPassword"
        assert decrypted_item.get("URI") == "www.example.com"
        assert decrypted_item.get("NOTES") == "top secret notes"


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

        assert decrypted_item.get("USER_ID") == 1
        assert decrypted_item.get("NAME") == "Fake Name"
        assert decrypted_item.get("USERNAME") == "Fake Username"
        assert decrypted_item.get("PASSWORD") == "asdf1234"
        assert decrypted_item.get("URI") == "www.google.com"
        assert decrypted_item.get("NOTES") == "note"


def test_update_encrypted_item(app):
    with app.app_context():
        assert (
            update_encrypted_item(
                user_ID="2",
                name="Updated item",
                username="Updated user",
                password="New-SuperPassword",
                uri="www.new-example.com",
                notes="New secret notes",
                folder_ID=3,
                item_ID=2,
            )
            == 2
        )
    with app.app_context():
        # check if the item is correctly inserted
        item = query_db("SELECT * FROM ITEM WHERE NAME = 'Updated item'", one=True)
        print(f"Item from database: {item}")
        assert item is not None

        decrypted_item = decrypt_item(item[0])
        print(f"Decrypted item: {decrypted_item}")
        assert decrypted_item is not None
        assert decrypted_item.get("USER_ID") == 2
        assert decrypted_item.get("NAME") == "Updated item"
        assert decrypted_item.get("USERNAME") == "Updated user"
        assert decrypted_item.get("PASSWORD") == "New-SuperPassword"
        assert decrypted_item.get("URI") == "www.new-example.com"
        assert decrypted_item.get("NOTES") == "New secret notes"


def test_delete_encrypted_item(app):
    with app.app_context():
        user_row = query_db(
            "SELECT ID FROM ITEM WHERE NAME = ?", ("Delete item",), one=True
        )
        print("ID of 'Delete item': ", user_row["ID"])
    with app.app_context():
        delete_encrypted_item(item_ID=user_row["ID"])
        user_row_deleted = query_db(
            "SELECT ID FROM ITEM WHERE NAME = ?", ("Delete item",), one=True
        )
        print("ID of 'Delete item': ", user_row_deleted)
        assert user_row_deleted is None


def test_get_folder_ID(app):
    with app.app_context():
        assert get_folder_ID("Example Folder", 1) == 1
    with app.app_context():
        assert get_folder_ID("Fail", "Fail") == None


def test_get_folder_name(app):
    with app.app_context():
        assert get_folder_name(1, 1) == "Example Folder"
    with app.app_context():
        assert get_folder_ID("Fail", "Fail") == None
