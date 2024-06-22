import os

from cryptography.fernet import Fernet
from sqlite3 import Error

from flask import current_app, flash

from app.db import get_db, query_db


def get_cipher():
    key = current_app.config[
        "ENCRYPTION_KEY"
    ].encode()  # or os.getenv('ENCRYPTION_KEY').encode()
    return Fernet(key)


def encrypt_data(data):
    cipher = get_cipher()
    if isinstance(data, str):
        data = data.encode()
    encrypted_data = cipher.encrypt(data)
    return encrypted_data


def decrypt_data(encrypted_data):
    cipher = get_cipher()
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data.decode()


def insert_encrypted_item(userID, name, username, password, uri, notes, folder_ID):
    conn = get_db()
    cursor = conn.cursor()

    try:
        encrypted_username = encrypt_data(username)
        encrypted_password = encrypt_data(password)
        encrypted_uri = encrypt_data(uri)
        encrypted_notes = encrypt_data(notes)

        cursor.execute(
            "INSERT INTO ITEM (USER_ID, name, username, password, uri, NOTES, FOLDER_ID) VALUES (?,?,?,?,?,?,?)",
            (
                userID,
                name,
                encrypted_username,
                encrypted_password,
                encrypted_uri,
                encrypted_notes,
                folder_ID,
            ),
        )
        conn.commit()
        inserted_id = cursor.lastrowid
        return inserted_id

    except Error as e:
        flash("Failed to save, please try again.")
        print("Database Error:", e)
        conn.rollback()

    except Exception as e:
        flash("Failed to save, please try again.")
        print("Exception:", e)

    finally:
        cursor.close()
        # conn.close()


def decrypt_item(item_ID):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT USER_ID, name, username, password, uri, NOTES, FOLDER_ID FROM ITEM WHERE ID = ?",
            (item_ID,),
        )
        row = cursor.fetchone()
        # Debug print row
        print(f"Printing selected row: {row}")
        if row:
            (
                userID,
                name,
                encrypted_username,
                encrypted_password,
                encrypted_uri,
                encrypted_notes,
                folderID,
            ) = row
            username = decrypt_data(encrypted_username)
            password = decrypt_data(encrypted_password)
            uri = decrypt_data(encrypted_uri)
            notes = decrypt_data(encrypted_notes)

            return {
                "ITEM_ID": item_ID,
                "USER_ID": userID,
                "NAME": name,
                "USERNAME": username,
                "PASSWORD": password,
                "URI": uri,
                "NOTES": notes,
                "FOLDER_ID": folderID,
            }
        else:
            return None

    except Error as e:
        print(f"An error occurred: {e}")
        return None
    # finally:
    #    cursor.close()
    #    conn.close()


def update_encrypted_item(item_id, user_id, name, username, password, uri, notes, folder_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        encrypted_username = encrypt_data(username)
        encrypted_password = encrypt_data(password)
        encrypted_uri = encrypt_data(uri)
        encrypted_notes = encrypt_data(notes)
        cursor.execute(
            """
            UPDATE ITEM
            SET NAME = ?, USERNAME = ?, PASSWORD = ?, URI = ?, NOTES = ?, FOLDER_ID = ?
            WHERE ID = ? AND USER_ID = ?
            """,
            (name, encrypted_username, encrypted_password, encrypted_uri, encrypted_notes, folder_id, item_id, user_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("Error updating item:", e)
        return False



def get_folder_ID(folder_name, user_ID):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM FOLDER WHERE LOWER(FOLDER_NAME) = LOWER(?) AND USER_ID = (?)",
            (
                folder_name,
                user_ID,
            ),
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        print("None found")
        return None
    except Error as e:
        print(f"An error occurred: {e}")
        return None
    # finally:
    #   cursor.close()
    #   conn.close()


def get_folder_name(folder_ID, user_ID):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT FOLDER_NAME FROM FOLDER WHERE USER_ID = (?) AND ID = (?)",
            (
                user_ID,
                folder_ID,
            ),
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        print("None found")
        return None
    except Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        cursor.close()
        # conn.close()


def delete_encrypted_item(item_ID, user_ID):
    conn = get_db()
    cursor = conn.cursor()
    try:
        before_delete = query_db("SELECT COUNT(*) AS before_delete FROM ITEM", one=True)

        cursor.execute(
            "DELETE FROM ITEM WHERE ID = ? AND USER_ID = ?",
            (
                item_ID,
                user_ID,
            ),
        )
        conn.commit()
        after_delete = query_db("SELECT COUNT(*) AS after_delete FROM ITEM", one=True)
        return before_delete[0] - after_delete[0]

    except Error as e:
        flash("Failed to delete, please try again.")
        print("Database Error:", e)
        conn.rollback()
        return None

    except Exception as e:
        flash("Failed to delete, please try again.")
        print("Exception:", e)
        return None

    finally:
        cursor.close()
        # conn.close()
