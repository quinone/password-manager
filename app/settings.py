# from _sqlite3 import Error
from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    flash,
    redirect,
    url_for,
    render_template,
)

# from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import ChangePasswordForm
from argon2 import PasswordHasher, exceptions


# from flask_login import login_required, current_user, LoginManager
from app.auth import login_required
from app.db import get_db

# from app.db_cryptography import decrypt_data, encrypt_data

# login_manager = LoginManager()
# login_manager.init_app(app)

bp = Blueprint(
    "settings", __name__, url_prefix="/settings", template_folder="templates"
)


@bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        user_id = session.get("user_id")
        vault_timeout = request.form.get("vaultTimeout", default="00:05:00")
        theme_id = request.form.get("themeId", default="light")
        settings_html = request.form.get(
            "settingsHtml", default=""
        )  # Get HTML content from the form

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "REPLACE INTO preferences (user_id, vault_timeout, theme_id, settings_html) VALUES (?, ?, ?, ?)",
                (
                    user_id,
                    vault_timeout,
                    theme_id,
                    settings_html,
                ),  # Use current_user.id to get user_id
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("Preferences saved successfully", "success")
        except Exception as e:
            flash(f"Failed to save preferences: {str(e)}", "danger")

        return redirect(url_for("settings.settings"))

    return render_template("settings.html")


@bp.route("/get_user_preferences", methods=["GET"])
@login_required
def get_user_preferences():
    current_user = session.get("user_id")
    try:
        preferences = (
            current_user.preferences
        )  # Assuming you have a preferences relationship in your User model
        if preferences:
            return jsonify(
                {
                    "vault_timeout": preferences.vault_timeout,
                    "theme_id": preferences.theme_id,
                    "settings_html": preferences.settings_html,
                }
            )
    except Exception as e:
        flash(f"Failed to fetch preferences: {str(e)}", "danger")

    # Return default preferences if no preferences found or an error occurred
    return jsonify(
        {"vault_timeout": "00:05:00", "theme_id": "light", "settings_html": ""}
    )


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        user_id = session.get("user_id")
        current_password = form.current_password.data
        new_password = form.new_password.data

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT PASSWORD FROM USER WHERE USER_ID = ?", (user_id,))
            row = cursor.fetchone()

            if row:
                current_password_hash = row[0]
                password_hasher = PasswordHasher()

                try:
                    password_hasher.verify(current_password_hash, current_password)
                    new_password_hash = password_hasher.hash(new_password)

                    cursor.execute(
                        "UPDATE USER SET PASSWORD = ? WHERE USER_ID = ?",
                        (new_password_hash, user_id),
                    )
                    conn.commit()
                    flash("Password updated successfully", "success")
                    return redirect(url_for("settings.settings"))
                except exceptions.VerifyMismatchError:
                    flash("Current password is incorrect", "danger")
                except Exception as e:
                    flash(f"Error updating password: {str(e)}", "danger")
                    print(f"Exception updating password: {str(e)}")
            else:
                flash("User not found", "danger")

        except Exception as e:
            flash("Database error: Failed to update password", "danger")
            print(f"Database error: {str(e)}")

        finally:
            cursor.close()
            conn.close()

    return render_template("change_password.html", form=form)


@bp.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "POST":
        current_password = request.form.get("currentPassword")
        user_id = session.get("user_id")

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT PASSWORD, EMAIL FROM USER WHERE USER_ID = ?", (user_id,)
            )
            row = cursor.fetchone()

            if row:
                stored_password_hash = row[0]
                email = row[1]
                password_hasher = PasswordHasher()

                try:
                    password_hasher.verify(stored_password_hash, current_password)
                    cursor.execute(
                        "DELETE FROM PREFERENCES WHERE USER_ID = ?", (user_id,)
                    )
                    cursor.execute("DELETE FROM ITEM WHERE USER_ID = ?", (user_id,))
                    cursor.execute("DELETE FROM FOLDER WHERE USER_ID = ?", (user_id,))
                    cursor.execute("DELETE FROM AUDIT WHERE USER_ID = ?", (user_id,))
                    cursor.execute("DELETE FROM USER WHERE USER_ID = ?", (user_id,))
                    conn.commit()

                    flash(
                        "Your account and all related data have been deleted successfully",
                        "success",
                    )
                    session.clear()
                    return redirect(url_for("auth.logout"))

                except exceptions.VerifyMismatchError:
                    flash("Incorrect password. Please try again.", "danger")
                    return redirect(url_for("settings.delete_account"))

            else:
                flash("User not found", "danger")
                return redirect(url_for("settings.settings"))

        except Exception as e:
            flash(f"Failed to delete account: {str(e)}", "danger")
            print(f"Exception deleting account: {str(e)}")

        finally:
            cursor.close()
            conn.close()

    return render_template("delete_account.html")
