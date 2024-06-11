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
from flask_login import login_required, current_user, LoginManager
from app.db import get_db
from tests.conftest import app

login_manager = LoginManager()
login_manager.init_app(app)

bp = Blueprint("settings", __name__, url_prefix="/setting", template_folder="templates")


@bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
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
                    current_user.id,
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
