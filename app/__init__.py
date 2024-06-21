import time
from datetime import datetime, timedelta
import os

from _sqlite3 import Error
from flask import (
    Flask,
    g,
    render_template,
    request,
    flash,
    url_for,
    session,
    redirect,
    logging,
    jsonify,
)
from flask_bootstrap import Bootstrap

from app.errors import page_not_found, internal_server_error

from app.forms import SearchForm

bootstrap = Bootstrap()


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="MUSTCHANGE",
        ENCRYPTION_KEY="3TirqVc7o7Fk7PzoMwUQCVCWS3ad4C2qArDxWV-Sej8=",  # Must change
        DATABASE=os.path.join(app.instance_path, "data-dev.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Imports db.py which includes get_db()
    from . import db, auth, vault, settings

    db.init_app(app)
    # Blueprint allows prefix in url like '/auth/' and points to the templates folder
    # and access the actions/methods in the auth.py by using auth.methods
    app.register_blueprint(auth.bp)
    app.register_blueprint(vault.bp)
    app.register_blueprint(settings.bp)
    bootstrap.init_app(app)

    # Error handling
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    app.secret_key = "super secret key"  # secret key for captcha

    # Define session timeout duration in seconds
    SESSION_TIMEOUT = 300

    # Set the session lifetime
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=5)

    @app.before_request
    def before_request():
        # Check if user is logged in and session is active
        if "user_id" in session:
            # Check if the last activity time is stored in session
            last_activity_time = session.get("last_activity_time")
            if last_activity_time is not None:
                # Calculate time elapsed since last activity
                time_elapsed = time.time() - last_activity_time
                # If time elapsed exceeds session timeout, log the user out
                if time_elapsed > SESSION_TIMEOUT:
                    # Clear session and log out user
                    session.clear()
                    flash("Session timed out due to inactivity.")
                    return redirect(url_for("login"))
            # Update last activity time in session
            session["last_activity_time"] = time.time()

            # Loading search form
            g.search_form = SearchForm()

    # Pass to base.html
    @app.context_processor
    def base():
        form = SearchForm()
        return dict(form=form)

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    @app.route("/", methods=["GET", "POST"])
    def index():
        return render_template("index.html")

    # Add this route to handle account deletion// not deleting data related to user just user profile
    @app.route("/delete_account", methods=["POST"])
    def delete_account():
        # Check if the user is authenticated
        if "user_id" in session:
            user_id = session["user_id"]
            conn = db.get_db()
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

    # Update your settings HTML template to include a form or button to trigger the account deletion

    return app
