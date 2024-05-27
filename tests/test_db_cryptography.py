from cryptography.fernet import Fernet
import pytest

from app.db_cryptography import get_cipher, encrypt_data, decrypt_data


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


def test_insert_encrypted_item():
    pass


def test_decrypt_item():
    pass