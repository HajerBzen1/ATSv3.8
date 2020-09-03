import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash

from app.database.operations import select

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = 'admin'
        password = request.form['password']
        error = None
        admin = select("Admin", "*", "username = %s", (username,), row_count=1)

        if not check_password_hash(admin[2], password):
            error = 'كلمة المرور غير صحيحة.'

        if error is None:
            session.clear()
            session['admin_id'] = admin[0]
            return redirect(url_for('launcher.launch'))

        flash(error)

    return render_template('login.html')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_admin():
    admin_id = session.get('admin_id')

    if admin_id is None:
        g.admin = None
    else:
        g.admin = select("Admin", "*", "id = %s", (admin_id,), row_count=1)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
