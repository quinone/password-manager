import functools
from _sqlite3 import Error
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from argon2 import PasswordHasher


from app.db import get_db


bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db()
            .execute("SELECT * FROM USER WHERE USER_ID = ?", (user_id,))
            .fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        email = request.form.get("email_address")
        name = request.form.get("name")
        password = request.form.get("password")
        password_hint = request.form.get("hint")
        retype_password = request.form.get("retype_password")  # Fix: Correct field name
        messages = []  # List to store messages
        message_type = "error"  # Default message type
        db = get_db()
        error = None
        # Validate form
        if not email:
            error = "Email address is required."
        if not password:
            error = "Password is required."
        if not name:
            error = "Name is required."
        if not password_hint:
            error = "Password hint is required."

        if error is None:
            try:
                # Establish database connection
                # conn = database.connect(db_file)
                conn = get_db()
                if conn is None:
                    raise Error("Failed to connect to the database.")
                cursor = conn.cursor()
                # Check if username already exists in the database

                cursor.execute(
                    "SELECT email FROM USER WHERE LOWER(email) = LOWER(?)", (email,)
                )
                existing_user = cursor.fetchone()
                if existing_user:
                    messages.append(
                        "Email already taken. Please choose a different email."
                    )
                    return render_template(
                        "register.html", messages=messages, message_type=message_type
                    )  # Return early
                # Check if password and password hint match
                if password == password_hint:
                    messages.append(
                        "Password hint should not be the same as the password."
                    )
                    return render_template(
                        "register.html", messages=messages, message_type=message_type
                    )  # Return early
                # Check password complexity
                if len(password) < 8:
                    messages.append("Password must be at least 8 characters long.")
                elif not any(char.isupper() for char in password):
                    messages.append(
                        "Password must contain at least one capital letter."
                    )
                elif not any(char in "!@#$%^&*?" for char in password):
                    messages.append("Password must contain at least one symbol.")
                else:
                    messages.append("Password meets complexity requirements.")
                    # Continue with USER process
                # Check if passwords match
                if password != retype_password:  # Fix: Correct field name
                    messages.append("Passwords do not match.")
                    return render_template(
                        "register.html", messages=messages, message_type=message_type
                    )  # Return early

                password_hasher = PasswordHasher()
                # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                hashed_password = password_hasher.hash(password)
                # Execute SQL query
                cursor.execute(
                    "INSERT INTO USER (EMAIL, NAME, PASSWORD, PASSWORD_HINT) VALUES (?, ?, ?, ?)",
                    (email, name, hashed_password, password_hint),
                )
                conn.commit()
                conn.commit()
                flash("Account created successfully.", "success")
                message_type = "success"
                return redirect(url_for("auth.login"))
            except Error as e:
                messages.append("Failed to signup. Try again!")
                print("Database Error:", e)
            except Exception as e:
                messages.append("Failed to create your account. Try again!")
                print("Error:", e)
            finally:
                if conn:
                    conn.close()
        flash(error, "danger")
        # Render the template with the messages and message type
        # return redirect(url_for("login"))
    return render_template("register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # Connect to the database
        conn = get_db()  # database.connect(db_file)
        if conn is None:
            flash("Failed to connect to the database.")
            return redirect(url_for("auth.login"))
        cursor = conn.cursor()
        # Check if user exists in the database
        cursor.execute("SELECT * FROM USER WHERE EMAIL = ?", (email,))
        user = cursor.fetchone()
        if user:
            # Debug: Print user data retrieved from the database
            print("User Data:", user)
            try:
                # Check if passwords match
                password_hasher = PasswordHasher()  # Using Argon2
                # if bcrypt.checkpw(password.encode('utf-8'), user[4]):  # Compare hashed password
                if password_hasher.verify(user["PASSWORD"], password):
                    # Passwords match, set session variables or redirect to dashboard
                    session.clear()
                    print(user["USER_ID"])
                    session["user_id"] = user[
                        "USER_ID"
                    ]  # Assuming user_id is in the first column
                    flash("Login successful.", "success")
                    return redirect(url_for("vault.profile"))
                else:
                    error_message = "Invalid email or password. Please try again."
            except Exception as e:
                error_message = "Invalid email or password. Please try again."
        else:
            error_message = "Invalid email or password. Please try again."
        # Debug: Print error message
        print("Error Message:", error_message)
        # Render login page with error message
        return render_template("index.html", error_message=error_message)
    return render_template("index.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "warning")
    return redirect(url_for("auth.login"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("You are not logged in.", "warning")
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


# to handle account deletion// not deleting data related to user just user profile
@bp.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    # Check if the user is authenticated
    if "user_id" in session:
        user_id = session["user_id"]
        conn = get_db()
        try:
            # Connect to the database
            # conn = database.connect(db_file)
            # cursor = conn.cursor()
            # TODO User should have to reauthenticate before deletion
            # Delete user's data from related tables
            conn.execute("DELETE FROM REGISTRATION WHERE USER_ID = ?", (user_id,))
            # You may need additional delete operations for related tables, such as items, folders, etc.

            conn.commit()
            flash("Your account has been successfully deleted.")
            # Clear the session
            session.clear()
            return redirect(url_for("index"))

        except Exception as e:
            # Handle any errors appropriately
            print("Error deleting account:", e)
            flash("Failed to delete your account. Please try again later.")

        finally:
            if conn:
                conn.close()
    else:
        # Redirect to login page or handle unauthorized access
        flash("You are not logged in.")
    return redirect(url_for("login"))
