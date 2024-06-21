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

from app.forms import ChangePasswordForm
from argon2 import PasswordHasher, exceptions
from app.auth import login_required
from app.db import get_db

bp = Blueprint(
    "settings", __name__, url_prefix="/settings", template_folder="templates"
)


@bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        user_id = session.get("user_id")
        vault_timeout = request.json.get("vaultTimeout", "00:05:00")
        theme_id = request.json.get("themeId", "light")

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "REPLACE INTO preferences (user_id, vault_timeout, theme_id) VALUES (?, ?, ?)",
                (user_id, vault_timeout, theme_id),
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"message": "Preferences saved successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to save preferences: {str(e)}"}), 500

    return render_template("settings.html")


@bp.route("/get_user_preferences", methods=["GET"])
@login_required
def get_user_preferences():
    user_id = session.get("user_id")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT vault_timeout, theme_id FROM preferences WHERE user_id = ?",
            (user_id,),
        )
        preferences = cursor.fetchone()
        cursor.close()
        conn.close()

        if preferences:
            vault_timeout, theme_id = preferences
            return jsonify({"vault_timeout": vault_timeout, "theme_id": theme_id})
        # Return default preferences if no preferences found or an error occurred
        return jsonify(
        {"vault_timeout": "00:05:00", "theme_id": "light", "settings_html": ""}
    )
    except Exception as e:
        return jsonify({"error": f"Failed to fetch preferences: {str(e)}"}), 500


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
