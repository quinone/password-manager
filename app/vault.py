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
        conn.execute(
            "SELECT FOLDER_NAME FROM FOLDER WHERE USER_ID = ? AND USER_ID = ? ",
            (user_id, user_id),
        )
        folders = conn.cursor().fetchall()
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
        folderID = form.folderID.data

        try:
            conn = get_db()
            conn.cursor().execute(
                "INSERT INTO ITEM (USER_ID, name, username, password, uri, NOTES, FOLDER_ID) VALUES (?,?,?,?,?,?,?)",
                (userID, name, username, password, uri, notes, folderID),
            )
            conn.commit()

            flash("Successfully submitted new item")
            return redirect(url_for("vault.vault"))
        except Error as e:
            flash("Failed to save, please try again.")
            print("Database Error:", e)
        except Exception as e:
            flash("Failed to save, please try again.")
            print("Exception:", e)
        finally:
            if conn:
                conn.close()
    return render_template("new-item.html", form=form)


""" Commented out to trial using flask-wtf extension
@bp.route("/new-item", methods=["GET", "POST"])
def new_item():
    if "user_id" in session:
        user_id = session.get("user_id")
        conn = get_db()
        if request.method == "POST":
            try:
                # Handle form submission
                item_type_id = request.form["item_type_id"]
                name = request.form["name"]
                folder_id = request.form.get("folder_id", False)

                # conn = database.connect(db_file)
                # cursor = conn.cursor()
                print("try to add item")
                conn.execute(
                    "INSERT INTO items (item_type_id, name, folder_id, user_id) VALUES (?, ?, ?, ?)",
                    (item_type_id, name, folder_id, user_id),
                )
                conn.commit()
                if conn:
                    conn.close()
                flash("Successfully submitted new item")
                return redirect(url_for("vault"))

            except Error as e:
                print("Database Error:", e)
                # Handle the error appropriately, e.g., render an error page
        # Retrieve folders belonging to the logged-in user
        # conn = database.connect(db_file)
        # cursor = conn.cursor()]
        flash("Please enter item to be saved")
        conn.execute("SELECT FOLDER_NAME FROM FOLDER WHERE USER_ID = ?", (user_id,))
        folders = conn.cursor().fetchall()
        print("Folders:", folders)
        conn.close()

        return render_template("new-item.html", folders=folders)

    # Redirect to login page or handle unauthorized access
    return redirect(url_for("auth.login"))

    # return render_template("new_item.html")

"""
"""@bp.route("/new_itemAction", methods=["GET", "POST"])
def new_itemAction():
    if "user_id" in session:
        user_id = session.get("user_id")
        conn = get_db()
        if request.method == "POST":
            try:
                # Handle form submission
                item_type_id = request.form["item_type_id"]
                name = request.form["name"]
                folder_id = request.form["folder_id"]

                # conn = database.connect(db_file)
                # cursor = conn.cursor()

                conn.execute(
                    "INSERT INTO items (item_type_id, name, folder_id, user_id) VALUES (?, ?, ?, ?)",
                    (item_type_id, name, folder_id, user_id),
                )
                conn.commit()

                if conn:
                    conn.close()

                return redirect(url_for("success_page"))

            except Error as e:
                print("Database Error:", e)
                # Handle the error appropriately, e.g., render an error page

        # Retrieve folders belonging to the logged-in user
        # conn = database.connect(db_file)
        # cursor = conn.cursor()
        conn.execute("SELECT FOLDER_NAME FROM FOLDER WHERE USER_ID = ?", (user_id,))
        folders = conn.fetchall()
        print("Folders:", folders)

        conn.close()

        return render_template("new_item.html", folders=folders)
    else:
        # Redirect to login page or handle unauthorized access
        return redirect(url_for("login_page"))"""


@bp.route("/new-folder")
@login_required
def new_folder():
    return render_template("new-folder.html")


@bp.route("/<folder_name>")
def view_folder(folder_name):
    conn = get_db()
    try:
        # Establish database connection
        # conn = database.connect(db_file)
        # cursor = conn.cursor()
        # Retrieve items from the selected folder
        conn.execute(
            "SELECT * FROM ITEM WHERE FOLDER_ID = (SELECT ID FROM FOLDER WHERE LOWER(FOLDER_NAME) = LOWER(?))",
            (folder_name,),
        )
        items = conn.cursor().fetchall()
    except conn.Error as e:
        print("Database Error:", e)
        items = []
    finally:
        # Close the database connection
        if conn:
            conn.close()
    # Render the template with the items in the folder
    return render_template("folder.html", folder_name=folder_name, items=items)


@bp.route("/add_folder", methods=["POST"])
def add_folder():
    folder_name = request.form.get("folder_name")
    messages = []  # List to store messages
    message_type = "error"  # Default message type
    conn = get_db()
    try:
        # Check if folder name is provided
        if not folder_name:
            messages.append("Please provide a folder name.")
        else:
            # Retrieve user ID from session
            user_id = session.get("user_id")
            if user_id:
                # Add folder to the database with the associated user_id
                conn.execute(
                    "INSERT INTO FOLDER (USER_ID, FOLDER_NAME) VALUES (?, ?)",
                    (user_id, folder_name),
                )
                conn.commit()
                messages.append("Folder added successfully.")
                message_type = "success"
            else:
                messages.append("User ID not found.")
    except Exception as e:
        messages.append("Failed to add folder. Try again!")
        print("Error:", e)

    finally:
        # Close the database connection
        if conn:
            conn.close()

    # Redirect back to the vault page after adding the folder
    return redirect(url_for("vault"))


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
