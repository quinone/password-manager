import string
from flask import Blueprint, session, flash, redirect, render_template, url_for, request

from app.PassGenerator import generate_number, generate_passphrase, generate_password, generate_username
from app.auth import login_required
from app.db import get_db, query_db
from app.db_cryptography import (
    get_folder_ID,
    insert_encrypted_item,
    decrypt_item,
    decrypt_data,
)
from app.forms import NewItemForm, SearchForm
from sqlite3 import Error

bp = Blueprint("vault", __name__, url_prefix="/vault", template_folder="templates")


def get_items_for_folder(folder_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, NAME, FOLDER_ID, USERNAME, PASSWORD, URI, NOTES FROM ITEM WHERE FOLDER_ID = ?",
            (folder_id,),
        )
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return items
    except Exception as e:
        flash("Error fetching items for folder: {}".format(str(e)), "danger")
        return []


# The rest of your routes and functions...


@bp.route("/")
@login_required
def vault():
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Retrieve folders
        user_id = session.get("user_id")
        cursor.execute(
            "SELECT FOLDER_NAME, ID FROM FOLDER WHERE USER_ID = ?", (user_id,)
        )
        folders = cursor.fetchall()

        # Retrieve items with no folder  along with decrypted data
        cursor.execute(
            "SELECT ID, NAME, FOLDER_ID, USERNAME, PASSWORD, URI, NOTES FROM ITEM WHERE FOLDER_ID IS NULL AND USER_ID = ?",
            (user_id,),
        )
        items = cursor.fetchall()

        # added here decryption
        decrypted_items = []
        for item in items:
            decrypted_item = {
                "ID": item["ID"],
                "NAME": item["NAME"],
                "FOLDER_ID": item["FOLDER_ID"],
                "USERNAME": decrypt_data(item["USERNAME"]),
                "PASSWORD": decrypt_data(item["PASSWORD"]),
                "URI": decrypt_data(item["URI"]),
                "NOTES": decrypt_data(item["NOTES"]),
            }
            decrypted_items.append(decrypted_item)

        cursor.close()
        conn.close()
        return render_template(
            "vault.html", folders=folders, items=decrypted_items, hide_password=True
        )
    except Exception as e:
        flash("Error fetching data: {}".format(str(e)), "danger")
        return render_template("vault.html", folders=[], items=[], hide_password=True)


@bp.route("/profile")
@login_required
def profile():
    user_id = session["user_id"]
    conn = get_db()
    if conn is None:
        flash("Failed to connect to the database.", "danger")
        return redirect(url_for("login"))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USER WHERE USER_ID = ?", (user_id,))
    user_info = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("profile.html", user_info=user_info)


@bp.route("/new-item", methods=["GET", "POST"])
@login_required
def new_item():
    form = NewItemForm(request.form)
    if request.method == "POST" and form.validate():
        userID = session.get("user_id")
        name = form.name.data
        username = form.username.data
        password = form.password.data
        uri = form.uri.data
        notes = form.notes.data
        folder_name = form.folder_name.data

        folder_ID = get_folder_ID(folder_name=folder_name, user_ID=userID)

        if insert_encrypted_item(
            userID, name, username, password, uri, notes, folder_ID
        ):
            flash("Successfully submitted new item", "success")
            return redirect(url_for("vault.vault"))

    return render_template("new-item.html", form=form)


@bp.route("/new-folder", methods=["GET", "POST"])
@login_required
def new_folder():
    if request.method == "POST":
        folder_name = request.form.get("folder_name")
        conn = get_db()
        try:
            if not folder_name:
                flash("Please provide a folder name.", "warning")
            else:
                user_id = session.get("user_id")
                if user_id:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO FOLDER (USER_ID, FOLDER_NAME) VALUES (?, ?)",
                        (
                            user_id,
                            folder_name,
                        ),
                    )
                    conn.commit()
                    flash("Folder added successfully.", "success")
                    return redirect(url_for("vault.vault"))
                else:
                    flash("User ID not found.", "danger")
        except Exception as e:
            flash("Failed to add folder. Try again!", "danger")
            print("Error:", e)
        finally:
            if conn:
                conn.close()
                print("Connection closed in new_folder()")
    return render_template("new-folder.html")


@bp.route("/folder/<folder_name>")
@login_required
def view_folder(folder_name):
    # Loads "user_id" in session:
    user_id = session["user_id"]
    # Verity folder exists
    folder_ID = get_folder_ID(folder_name=folder_name, user_ID=user_id)
    if folder_ID == None:
        flash("You don't have a folder with that name.", "danger")
        return redirect(url_for("vault.vault"))
    decrypted_items = []
    try:
        # Fetch item IDs based on the folder ID
        item_IDs = query_db("SELECT ID FROM ITEM WHERE FOLDER_ID = ?", (folder_ID,))
        if item_IDs:
            print(f"Item IDs: {item_IDs}")
            for item in item_IDs:
                item_ID = item[0]

                decrypted_item = decrypt_item(item_ID)
                if decrypt_item:
                    decrypted_items.append(decrypted_item)
                print(f"Items:", decrypted_items)

    except Error as e:
        print("Database Error:", e)

    return render_template(
        "folder.html", folder_name=folder_name, items=decrypted_items
    )


@bp.route("/search", methods=["POST"])
@login_required
def search():
    form = SearchForm()
    user_ID = session["user_id"]
    decrypted_items = []
    if form.validate_on_submit():
        try:
            searched = form.searched.data
            item_IDs = query_db(
                "SELECT ID FROM ITEM WHERE USER_ID = ? AND LOWER(NAME) LIKE LOWER(?)",
                (
                    user_ID,
                    f"%{searched}%",
                ),
            )
            if item_IDs:
                for item in item_IDs:
                    item_ID = item[0]
                    decrypted_item = decrypt_item(item_ID)
                    if decrypt_item:
                        decrypted_items.append(decrypted_item)
            else:
                flash("No matching results.", "warning")

        except Error as e:
            flash("Database Error: {}".format(str(e)), "danger")

        return render_template(
            "search.html", form=form, searched=searched, items=decrypted_items
        )
    return redirect(url_for("vault.vault"))


@bp.route("/generate-password", methods=["GET", "POST"])
# @login_required
def password_generator():
    # def handle_generate_password():
    if request.method == "POST":
        length = int(request.form.get("total_length", 15))
        min_capitals = int(request.form.get("min_capitals"))
        min_numbers = int(request.form.get("min_numbers", 0))
        min_special_chars = int(request.form.get("min_special_chars", 0))
        special_chars = []
        password_type = request.form.get("password_type")
        # Handle options
        options = request.form.get("options")
        if options == 'username':
            username = generate_username()
            return render_template("password-generator.html", generated_password=username)
        if options == 'password':
            if password_type == "password":
                special_chars = request.form.getlist("special_chars")
                # Generate password with alphabetic characters, numbers, and selected special characters
                special_chars = "".join(special_chars)
                # characters = string.ascii_letters + string.digits + special_chars
                password = generate_password(
                    length=length,
                    number_digits=min_numbers,
                    number_upper=min_capitals,
                    number_special=min_special_chars,
                    special=special_chars,
                )
                # return render_template("password-generator.html", generated_password=password)
            if password_type == "pin":
                password = generate_number(length)
            if password_type == "passphrase":
                password = generate_passphrase(length=length)
            return render_template("password-generator.html", generated_password=password)
    return render_template("password-generator.html")
