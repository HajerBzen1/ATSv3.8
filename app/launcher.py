from flask import Blueprint, render_template, url_for, redirect, flash, request

from ATSLegal.Entities.Summary import Summary
from app import app
from app.auth import login_required
from app.database.db_controller import get_stored_summaries, delete_summary

bp = Blueprint('launcher', __name__)

app.config["CURRENT"] = 0
app.config["CASES"] = []
app.config["STORED"] = []


@bp.route('/', methods=('GET', 'POST'))
@login_required
def launch():
    app.config["CASES"], app.config["STORED"] = get_stored_summaries()
    try:
        summary = app.config["STORED"][app.config["CURRENT"]]
    except:
        summary = None
        if not app.config['STORED']:
            flash('لا يوجد ملخصات محفوظة!')
    return render_template('launcher.html', files=app.config["CASES"], summary=summary)


@bp.route('/summary', methods=('GET', 'POST'))
@login_required
def get_summary():
    if request.method == 'POST':
        try:
            app.config["CURRENT"] = app.config["CASES"].index(request.form['filename'])
        except:
            pass
    return redirect(url_for('launcher.launch'))


@bp.route('/modify', methods=('GET', 'POST'))
@login_required
def modify():
    if request.method == 'POST':
        if app.config['STORED']:
            current = app.config['STORED'][app.config["CURRENT"]]
            content = ''
            for s in current['original']:
                content += '\n'.join(current['original'][s])
            summary = Summary(content, current['filename'])

            app.config['NEW_SUM'] = [summary]
            app.config['id'] = current["id"]
            app.config['FILES'] = [app.config['CASES'][app.config["CURRENT"]]]
            app.config["CURRENT"] = 0
            app.config['NEW'] = False
            return redirect(url_for('summarizer.summarizer'))
    return redirect(url_for('launcher.launch'))


@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    if request.method == 'POST':
        if len(app.config['STORED']) > 0:
            summary = app.config['STORED'][app.config["CURRENT"]]
            delete_summary(summary['id'])
            if app.config["CURRENT"] > 0:
                app.config["CURRENT"] -= 1
    return redirect(url_for('launcher.launch'))
