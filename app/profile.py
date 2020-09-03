from flask import Blueprint, render_template, flash, request, g, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import login_required
from app.database.operations import update

bp = Blueprint('profile', __name__)


@bp.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    return render_template('profile.html')


@bp.route('/profile_save', methods=('GET', 'POST'))
@login_required
def profile_save():
    if request.method == 'POST':
        error = None
        password = request.form.get("password")
        new_password = request.form.get("new_password")

        id = g.admin[0]
        if not check_password_hash(g.admin[2], password):
            error = 'كلمة المرور غير صحيحة.'
        else:
            if new_password and new_password != password:
                update("Admin", ["password"],
                       (generate_password_hash(new_password),), ['id'], (id,))

        if error:
            flash(error)
            return redirect(url_for('profile.profile'))
        elif new_password:
            return redirect(url_for("auth.logout"))
        return redirect(url_for("launcher.launch"))
    return redirect(url_for('profile.profile'))
