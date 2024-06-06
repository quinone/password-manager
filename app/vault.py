from flask import (
    Blueprint,
    session,
    flash,
    redirect,
    render_template,
    url_for,
    request
)

from app.auth import login_required
from app.db import get_db, query_db
from app.db_cryptography import get_folder_ID, insert_encrypted_item, decrypt_item
from app.forms import NewItemForm, SearchForm
from sqlite3 import Error

bp = Blueprint("vault", __name__, url_prefix="/vault", template_folder="templates")

def get_items_with_no_folder():
    user_id = session.get("user_id")
    print("==================================================.")
    print("User ID:", user_id)
    try:
        conn = get_db()
        if conn is None:
            print("Connection is None")
        print("Connection to the database established.")
        cursor = conn.cursor()
        print("Cursor opened ")
        cursor.execute("SELECT ID, NAME, FOLDER_ID, USERNAME, PASSWORD, URI, NOTES FROM ITEM WHERE FOLDER_ID IS NULL AND USER_ID = ?", (user_id,))
        print("executed query  ")
        items = cursor.fetchall()
        for item in items:
            print(item)  # Print each item to the console
        cursor.close()
        print("Cursor closed ")
        conn.close()
        print("Connection closed get_items_with_no_folder.")
        print("===========================================================")
        return items
    except Exception as e:
        print("Error:", e)  # Print the exception to see what's going wrong
        flash("Error fetching items with no folder: {}".format(str(e)), "danger")
        return []


def get_all_folders():
    user_id = session.get("user_id")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT FOLDER_NAME, ID FROM FOLDER WHERE USER_ID = ?", (user_id,))
        folders = cursor.fetchall()
        cursor.close()
        conn.close()
        print("Connection closed in get_all_folders()")
        return folders
    except Exception as e:
        flash("Error fetching folders: {}".format(str(e)), "danger")
        return []


def get_items_for_folder(folder_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, NAME, FOLDER_ID, USERNAME, PASSWORD, URI, NOTES FROM ITEM WHERE FOLDER_ID = ?", (folder_id,))
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        print("Connection closed in get_items_for_folder()")
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
        cursor.execute("SELECT FOLDER_NAME, ID FROM FOLDER WHERE USER_ID = ?", (user_id,))
        folders = cursor.fetchall()

        # Retrieve items with no folder
        cursor.execute(
            "SELECT ID, NAME, FOLDER_ID, USERNAME, PASSWORD, URI, NOTES FROM ITEM WHERE FOLDER_ID IS NULL AND USER_ID = ?",
            (user_id,))
        items = cursor.fetchall()

        cursor.close()
        conn.close()

        print("Connection closed in vault()")

        return render_template("vault.html", folders=folders, items=items)
    except Exception as e:
        flash("Error fetching data: {}".format(str(e)), "danger")
        return render_template("vault.html", folders=[], items=[])


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
    print("Connection closed in profile()")
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

        if insert_encrypted_item(userID, name, username, password, uri, notes, folder_ID):
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

@bp.route("/folder/<int:folder_id>/<string:folder_name>")
@login_required
def view_folder(folder_id, folder_name):
    items = get_items_for_folder(folder_id)
    return render_template('folder.html', items=items, folder_id=folder_id, folder_name=folder_name)

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

        return render_template("search.html", form=form, searched=searched, items=decrypted_items)
    return redirect(url_for("vault.vault"))
