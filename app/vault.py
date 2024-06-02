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
from app.db_cryptography import insert_encrypted_item
from app.forms import NewItemForm

bp = Blueprint("vault", __name__, url_prefix="/vault", template_folder="templates")

@bp.route("/")
@login_required
def vault():
    user_id = session.get("user_id")
    folders = []
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT FOLDER_NAME FROM FOLDER WHERE USER_ID = ?",
            (user_id,),
        )
        folders = cursor.fetchall()
    except Exception as e:
        print("Error:", e)
    finally:
        if conn:
            conn.close()
    return render_template("vault.html", folders=folders)

@bp.route("/profile")
@login_required
def profile():
    user_id = session["user_id"]
    conn = get_db()
    if conn is None:
        flash("Failed to connect to the database.")
        return redirect(url_for("auth.login"))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USER WHERE USER_ID = ?", (user_id,))
    user_info = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("profile.html", user_info=user_info)


@bp.route("/new-item", methods=["GET", "POST"])
@login_required
def new_item():
    form = NewItemForm()

    user_id = session.get("user_id")
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ID, FOLDER_NAME FROM FOLDER WHERE USER_ID = ?", (user_id,))
        folders = cursor.fetchall()
        form.folderID.choices = [(str(folder[0]), folder[1]) for folder in folders]
    except Exception as e:
        print("Error loading folders:", e)
        flash("Failed to load folders. Please try again later.", "error")

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        password = form.password.data
        uri = form.uri.data
        notes = form.notes.data
        folderID = form.folderID.data

        try:
            cursor.execute(
                "INSERT INTO ITEM (USER_ID, FOLDER_ID, NAME, USERNAME, PASSWORD, URI, NOTES) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, folderID, name, username, password, uri, notes)
            )
            conn.commit()
            flash("Item added successfully.", "success")
            return redirect(url_for("vault.vault"))
        except Exception as e:
            flash("Failed to add item. Try again!", "error")
            print("Error adding item:", e)
        finally:
            cursor.close()
            conn.close()
    else:
        conn.close()  # Close the connection after loading the form choices if not a POST request

    return render_template("new-item.html", form=form)





@bp.route("/new-folder")
@login_required
def new_folder():
    return render_template("new-folder.html")

@bp.route("/<folder_name>")
@login_required
def view_folder(folder_name):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ITEM WHERE FOLDER_ID = (SELECT ID FROM FOLDER WHERE LOWER(FOLDER_NAME) = LOWER(?))",
            (folder_name,),
        )
        items = cursor.fetchall()
    except conn.Error as e:
        print("Database Error:", e)
        items = []
    finally:
        if conn:
            conn.close()
    return render_template("folder.html", folder_name=folder_name, items=items)


@bp.route("/add_folder", methods=["POST"])
@login_required
def add_folder():
    folder_name = request.form.get("folder_name")
    messages = []
    message_type = "error"
    conn = get_db()
    try:
        if not folder_name:
            messages.append("Please provide a folder name.")
        else:
            user_id = session.get("user_id")
            if user_id:
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
        if conn:
            conn.close()
    return redirect(url_for("vault.vault"))

@bp.route("/add_item", methods=["POST"])
@login_required
def add_item():
    form = NewItemForm(request.form)
    if request.method == "POST" and form.validate():
        userID = session.get("user_id")
        name = form.name.data
        username = form.username.data
        password = form.password.data
        uri = form.uri.data
        notes = form.notes.data
        folderID = form.folderID.data

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO ITEM (USER_ID, FOLDER_ID, NAME, USERNAME, PASSWORD, URI, NOTES) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (userID, folderID, name, username, password, uri, notes),
            )
            conn.commit()
            flash("Item added successfully.", "success")
        except Exception as e:
            flash("Failed to add item. Try again!", "error")
            print("Error:", e)
        finally:
            if conn:
                conn.close()
        return redirect(url_for("vault.vault"))
    return render_template("new-item.html", form=form)
