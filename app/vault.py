from flask import (
    Blueprint,
    session,
    url_for,
    flash,
    redirect,
    render_template,
)

from app.db import get_db

bp = Blueprint("vault", __name__, url_prefix="/vault", template_folder="templates")

@bp.route("/")
def vault():
   if "user_id" in session:
       user_id = session.get("user_id")
       try:
           # Establish database connection
           conn = get_db() #database.connect(db_file)
           cursor = conn.cursor()
           # Retrieve folders for the current user
           cursor.execute(
               "SELECT FOLDER_NAME FROM FOLDER WHERE USER_ID = ? AND USER_ID = ? ",
               (user_id, user_id),
           )
           folders = cursor.fetchall()
       except Exception as e:
           print("Error:", e)
           folders = []
       finally:
           # Close the database connection
           if conn:
               conn.close()
       # Render the template with the list of folders
       return render_template("vault.html", folders=folders)
   flash("You are not logged in.")
   return redirect(url_for("login"))


@bp.route("/profile")
def profile():
    # Check if user is logged in
    if "user_id" in session:
        user_id = session["user_id"]
        # Connect to the database
        conn = get_db() #database.connect(db_file)
        if conn is None:
            flash("Failed to connect to the database.")
            return redirect(url_for("login"))
        cursor = conn.cursor()
        # Fetch user info from the database
        cursor.execute("SELECT * FROM USER WHERE USER_ID = ?", (user_id,))
        user_info = cursor.fetchone()
        # Close cursor and connection
        cursor.close()
        conn.close()
        return render_template("profile.html", user_info=user_info)
    flash("You are not logged in.")
    return redirect(url_for("login"))