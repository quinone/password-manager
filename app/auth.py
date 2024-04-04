import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from argon2 import PasswordHasher


from app.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM USER WHERE USER_ID = ?", (user_id)).fetchone()
        )


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        hint = request.form['hint']
        db = get_db()
        error = None

        if not email:
            error = 'Email address is required.'

        if not password:
            error = 'Password is required.'
        if not name:
            error = 'Name is required.'
        if not hint:
            error = 'Password hint is required.'

        if error is None:
            try:
                password_hasher = PasswordHasher()
                db.execute(
                    "INSERT INTO USER (email, password, name, password_hint) VALUES (?, ?, ?,?)",
                    (email, password_hasher.hash(password), name, hint),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)
    return render_template('register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute("SELECT * FROM USER WHERE EMAIL = ?", (email,)).fetchone()

        password_hasher = PasswordHasher()
        if user is None:
            error = 'Incorrect username or password'
        elif not password_hasher.verify(user['PASSWORD'], password):
            error = 'Incorrect username or password'

        if error is None:
            session.clear()
            session['user_id'] = user['USER_ID']
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
