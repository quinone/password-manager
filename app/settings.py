from flask import Blueprint, jsonify, request, session, flash, redirect, url_for, render_template
from flask_login import login_required
from app.db import get_db

bp = Blueprint("settings", __name__, url_prefix="/settings", template_folder="templates")


@bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        user_id = session.get("user_id")
        vault_timeout = request.form.get("vaultTimeout", default="00:05:00")
        theme_id = request.form.get("themeId", default="light")

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "REPLACE INTO preferences (user_id, vault_timeout, theme_id) VALUES (?, ?, ?)",
                (user_id, vault_timeout, theme_id)
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
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT vault_timeout, theme_id FROM preferences WHERE user_id = ?", (user_id,))
    preferences = cursor.fetchone()
    cursor.close()
    conn.close()

    if preferences:
        return jsonify({
            "vault_timeout": preferences[0],
            "theme_id": preferences[1]
        })
    else:
        return jsonify({
            "vault_timeout": "00:05:00",
            "theme_id": "light"
        })
