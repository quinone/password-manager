import logging
from flask import Blueprint, jsonify, request, session, flash, redirect, url_for, render_template
from app.auth import login_required
from app.db import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to log actions


bp = Blueprint("settings", __name__, url_prefix="/settings", template_folder="templates")

def get_audit_data(user_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ENTITY_TYPE_ID, ENTITY_ID, ACTION_TYPE, TIMESTAMP
            FROM AUDIT
            WHERE USER_ID = ? OR USER_ID IS NULL
            ORDER BY TIMESTAMP DESC
            LIMIT 30
            """,
            (user_id,)
        )
        audit_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return audit_data
    except Exception as e:
        logger.error(f"Failed to fetch audit data: {e}")
        return []

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
            log_action(user_id, f"Updated preferences: vault_timeout={vault_timeout}, theme_id={theme_id}")
            return jsonify({"message": "Preferences saved successfully"}), 200
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return jsonify({"error": f"Failed to save preferences: {str(e)}"}), 500

    user_id = session.get("user_id")
    user_name = session.get("user_name")  # Get the user's name from session
    audit_data = get_audit_data(user_id)
    return render_template("settings.html", audit_data=audit_data, user_name=user_name)

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
        logger.error(f"Failed to fetch preferences: {e}")
        return jsonify({"error": f"Failed to fetch preferences: {str(e)}"}), 500
