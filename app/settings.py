from flask import Blueprint, jsonify, request, session, flash, redirect, url_for, render_template
from app.auth import login_required
from app.db import get_db

bp = Blueprint("settings", __name__, url_prefix="/settings", template_folder="templates")

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
        else:
            return jsonify({"vault_timeout": "00:05:00", "theme_id": "light"})
    except Exception as e:
        return jsonify({"error": f"Failed to fetch preferences: {str(e)}"}), 500
