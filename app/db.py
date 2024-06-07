import sqlite3

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def query_db(query, args=(), one=False):
    cursor = get_db().execute(query, args)
    results = cursor.fetchall()
    cursor.close()
    return (results[0] if results else None) if one else results

# In app/db.py
from flask import current_app

def get_folder_id_from_database(folder_name):
    try:
        with current_app.app_context():
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT ID FROM FOLDER WHERE FOLDER_NAME = ?", (folder_name,))
            folder_id = cursor.fetchone()
            cursor.close()
            conn.close()
            return folder_id[0] if folder_id else None
    except Exception as e:
        # Handle exceptions, such as database errors
        print(f"Error fetching folder_id for folder_name '{folder_name}': {e}")
        return None
