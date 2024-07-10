import logging
from datetime import timedelta
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

import app
from app.forms import ChangePasswordForm
from argon2 import PasswordHasher, exceptions
from app.auth import login_required, log_action  # Ensure log_action is imported
from app.db import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint("settings", __name__, url_prefix="/settings", template_folder="templates")

def get_audit_data(user_id):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ENTITY_TYPE_ID, ENTITY_ID, ACTION_TYPE, TIMESTAMP
            FROM AUDIT
            WHERE USER_ID = ?
            ORDER BY TIMESTAMP DESC
            LIMIT 30
            """,
            (user_id,)
        )
        audit_data = cursor.fetchall()
        # Ensuring data is in dictionary format for templates
        formatted_audit_data = [
            {
                'TIMESTAMP': row[3],
                'ACTION_TYPE': row[2],
                'ENTITY_ID': row[1],
            }
            for row in audit_data
        ]
        return formatted_audit_data
    except Exception as e:
        logger.error(f"Failed to fetch audit data: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@bp.route('/', methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        user_id = session.get("user_id")
        vault_timeout = request.json.get("vaultTimeout", "00:05:00")
        theme_id = request.json.get("themeId", "light")

        # Convert vault_timeout to seconds
        vault_timeout_seconds = sum(
            int(x) * 60 ** i for i, x in enumerate(reversed(vault_timeout.split(':')))
        )
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
            log_action(user_id, None, "UPDATED_PREFERENCES")

            # Store the vault_timeout in session
            session['vault_timeout'] = vault_timeout_seconds
            app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=vault_timeout_seconds)

            return jsonify({"message": "Preferences saved successfully"}), 200
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return jsonify({"error": f"Failed to save preferences: {str(e)}"}), 500

    user_id = session.get("user_id")
    audit_data = get_audit_data(user_id)
    logger.debug(f"Audit Data: {audit_data}")  # Debug line to check audit_data
    return render_template("settings.html", audit_data=audit_data)

@bp.route("/get_user_preferences", methods=["GET"])
@login_required
def get_user_preferences():
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT vault_timeout, theme_id FROM preferences WHERE user_id = ?",
            (user_id,),
        )
        preferences = cursor.fetchone()

        if preferences:
            vault_timeout, theme_id = preferences
            return jsonify({"vault_timeout": vault_timeout, "theme_id": theme_id})
        # Return default preferences if no preferences found or an error occurred
        return jsonify(
            {"vault_timeout": "00:05:00", "theme_id": "light"}
        )
    except Exception as e:
        return jsonify({"error": f"Failed to fetch preferences: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user_id = session.get("user_id")
        current_password = form.current_password.data
        new_password = form.new_password.data

        try:
            conn = get_db()
            cursor = conn.cursor()
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
                    log_action(user_id, None, "PASSWORD CHANGED")
                    return redirect(url_for("settings.settings"))
                except exceptions.VerifyMismatchError:
                    flash("Current password is incorrect", "danger")
                except Exception as e:
                    flash(f"Error updating password: {str(e)}", "danger")
                    logger.error(f"Exception updating password: {str(e)}")
            else:
                flash("User not found", "danger")

        except Exception as e:
            flash("Database error: Failed to update password", "danger")
            logger.error(f"Database error: {str(e)}")

        cursor.close()
        conn.close()

    return render_template("change_password.html", form=form)


@bp.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "POST":
        current_password = request.form.get("currentPassword")
        user_id = session.get("user_id")

        conn = None
        cursor = None

        try:
            conn = get_db()
            cursor = conn.cursor()
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
                    log_action(user_id, None, "DELETE_ACCOUNT")
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
            logger.error(f"Exception deleting account: {str(e)}")

        cursor.close()
        conn.close()

    return render_template("delete_account.html")