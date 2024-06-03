from sqlite3 import Error
from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    url_for,
    flash,
    redirect,
    render_template,
)

from app.auth import login_required
from app.db import get_db
from app.db_cryptography import decrypt_item, get_folder_ID, insert_encrypted_item
from app.forms import NewItemForm

bp = Blueprint("vault", __name__, url_prefix="/vault", template_folder="templates")


@bp.route("/")
@login_required
def vault():
    user_id = session.get("user_id")
    try:
        # Establish database connection
        conn = get_db()  # database.connect(db_file)
        # cursor = conn.cursor()
        # Retrieve folders for the current user
        cursor = conn.cursor()
        cursor.execute(
            "SELECT FOLDER_NAME FROM FOLDER WHERE USER_ID = ? ",
            (user_id,),
        )
        folders = cursor.fetchall()
    except Exception as e:
        print("Error:", e)
        folders = []
    finally:
        # Close the database connection
        if conn:
            conn.close()
    # Render the template with the list of folders
    return render_template("vault.html", folders=folders)


@bp.route("/profile")
@login_required
def profile():
    # Loads "user_id" in session:
    user_id = session["user_id"]
    # Connect to the database
    conn = get_db()  # database.connect(db_file)
    if conn is None:
        flash("Failed to connect to the database.")
        return redirect(url_for("login"))
    cursor = conn.cursor()
    # Fetch user info from the database
    cursor.execute("SELECT * FROM USER WHERE USER_ID = ?", (user_id,))
    user_info = cursor.fetchone()
    # Close cursor and connection
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

        # Get folder_ID from folder_name
        folder_ID = get_folder_ID(folder_name=folder_name,user_ID=userID)

        if insert_encrypted_item(
            userID, name, username, password, uri, notes, folder_ID
        ):
            flash("Successfully submitted new item")
            return redirect(url_for("vault.vault"))

    return render_template("new-item.html", form=form)


@bp.route("/<folder_name>")
@login_required
def view_folder(folder_name):
    # Loads "user_id" in session:
    user_id = session["user_id"]
    # Verity folder exists
    folder_ID = get_folder_ID(folder_name=folder_name,user_ID=user_id)
    conn = get_db()
    decrypted_items = []
    try:
        cursor = conn.cursor()
        # Fetch item IDs based on the folder ID
        cursor.execute("SELECT ID FROM ITEM WHERE FOLDER_ID = ?", (folder_ID,))
        item_IDs = cursor.fetchall()
        if item_IDs:
            print(f"Item IDs: {item_IDs}")
            for item in item_IDs:
                item_ID = item[0]

                decrypted_item = decrypt_item(item_ID)
                if decrypt_item:
                    decrypted_items.append(decrypted_item)
                print(f"Items:", decrypted_items)
            print("success")
        #return render_template("folder.html", folder_name=folder_name, items=decrypted_items)

    except conn.Error as e:
        print("Database Error:", e)

    return render_template(
        "folder.html", folder_name=folder_name, items=decrypted_items
    )


@bp.route("/new-folder", methods=["GET", "POST"])
@login_required
def new_folder():
    if request.method == "POST":
        folder_name = request.form.get("folder_name")
        messages = []
        message_type = "error"
        conn = get_db()
        try:
            if not folder_name:
                flash("Please provide a folder name.")
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
    return render_template("new-folder.html")


@bp.route("/get_folders1")
def get_folders():
    # Assuming you have a function to retrieve folders from the database
    folders = (
        database.get_folders()
    )  # Implement this function according to your database schema

    # Assuming each folder is represented as a dictionary with 'folder_id' and 'folder_name' keys
    folders_data = [
        {"folder_id": folder["folder_id"], "folder_name": folder["folder_name"]}
        for folder in folders
    ]
    # Return the folder data as JSON
    return jsonify(folders_data)
