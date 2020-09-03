from flask import Blueprint, render_template, flash, request, redirect, url_for

from app import app
from app.auth import login_required
from app.database.operations import insert, select, update, delete
from app.database.db_controller import get_separators

bp = Blueprint('expressions', __name__)
app.config['SEPARATORS'] = []


@bp.route('/expressions', methods=('GET', 'POST'))
@login_required
def expressions():
    app.config['SEPARATORS'] = get_separators()
    try:
        separators = [e[1] for e in app.config['SEPARATORS']]
    except:
        separators = None
        flash("لا يوجد عبارات تقسيم!")
    return render_template('expressions.html', expressions=separators)


@bp.route('/save', methods=('GET', 'POST'))
@login_required
def save():
    e = 0
    for name in request.form:
        if e < len(app.config['SEPARATORS']):
            if request.form[name]:
                if request.form[name] != app.config['SEPARATORS'][e][1]:
                    update("Separator", ["expression"], (request.form[name],),
                           ["id"], (app.config['SEPARATORS'][e][0],))
            else:
                delete("Separator", ["id"], (app.config['SEPARATORS'][e][0],))
        elif request.form[name]:
            insert("Separator", ["expression"], (request.form[name],))
        e += 1

    return redirect(url_for('summarizer.summarizer'))

