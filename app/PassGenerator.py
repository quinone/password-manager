import os
import string
import random
from flask import (
    Blueprint,
    g,
    request,
    flash,
    session,
    redirect,
    render_template,
    url_for,
    jsonify,
)
from app.forms import SearchForm
from app.auth import login_required
from app.db import get_db

bp = Blueprint("password_generator", __name__, url_prefix="/password_generator", template_folder="templates")


def generate_password(
        length, min_length, min_numbers, min_special_chars, special_chars, avoid_ambiguous
):
    password = ""
    numbers = string.digits
    special_characters = "".join(special_chars)
    ambiguous_characters = "0Oo1Il|"
    if avoid_ambiguous:
        characters = "".join(
            [
                c
                for c in string.ascii_letters + numbers + special_characters
                if c not in ambiguous_characters
            ]
        )
    else:
        characters = string.ascii_letters + numbers + special_characters

    # Add minimum numbers
    for _ in range(min_numbers):
        password += random.choice(numbers)

    # Add minimum special characters
    for _ in range(min_special_chars):
        password += random.choice(special_characters)

    # Generate the rest of the password
    remaining_length = length - len(password)
    for _ in range(remaining_length):
        password += random.choice(characters)

    password = "".join(random.sample(password, len(password)))
    return password


@bp.route("/generate_password", methods=["POST"])
@login_required
def handle_generate_password():
    length = int(request.form.get("total_length", 15))
    min_length = int(request.form.get("min_length", 10))
    min_numbers = int(request.form.get("min_numbers", 0))
    min_special_chars = int(request.form.get("min_special_chars", 0))
    special_chars = []
    avoid_ambiguous = "avoid_ambiguous" in request.form

    # Handle options
    options = request.form.get("options")
    if options == "Password":
        total_length = int(request.form.get("total_length", 15))  # Default total length to 15
        min_length = int(request.form.get("min_length", 10))  # Default minimum length to 10

        # Check if total length is less than 15
        if total_length < 15:
            flash("Total length should be 15 or more.")
        # Check if minimum length is less than 10
        elif min_length < 10:
            flash("Minimum length should be 10 or more.")
        else:
            password_type = request.form.get("password_type")
            special_chars = request.form.getlist("special_chars")

            if password_type == "Alphanumeric":
                # If no special characters
                # If no special characters are selected, show a Flask message
                if not special_chars:
                    flash("Please select some special characters.")
                else:
                    # Generate password with alphabetic characters, numbers, and selected special characters
                    special_chars = "".join(special_chars)
                    characters = string.ascii_letters + string.digits + special_chars
                    password = generate_password(total_length, min_length, min_length, min_length, characters,
                                                 False)
            elif password_type == "Alphabetic":
                # Generate password with only alphabetic characters
                characters = string.ascii_letters
                password = generate_password(total_length, min_length, min_length, min_length, characters, False)
            elif password_type == "Numeric":
                # Generate password with only numeric characters
                characters = string.digits
                password = generate_password(total_length, min_length, min_length, min_length, characters, False)

            password = generate_password(
                length,
                min_length,
                min_numbers,
                min_special_chars,
                special_chars,
                avoid_ambiguous,
            )
            return jsonify(password=password)


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        return handle_generate_password()

    return render_template("index.html")


@bp.route("/gen_Password")
@login_required
def gen_Password():
    return render_template("gen_Password.html")


@bp.route("/password_generator")
@login_required
def password_generator():
    return render_template("Password_generator.html")


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

