import os

from flask import Blueprint, render_template, flash, url_for, redirect, request
from werkzeug.utils import secure_filename

from ATSLegal import FileProcess as tp
from ATSLegal.Entities.Summary import Summary

from app import app

from app.auth import login_required
from app.database.db_controller import update_summary, get_separators, save_summary

bp = Blueprint('summarizer', __name__)

UPLOAD_FOLDER = os.getcwd() + '/app/tmp'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['CURRENT'] = 0
app.config['FILES'] = []
app.config['NEW_SUM'] = []
app.config['NEW'] = True
app.config['THRESHOLD'] = (100, '%')
app.config['SEPARATORS'] = None

ALLOWED_EXTENSIONS = ["txt", "pdf"]


# check if a file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/summarizer', methods=('GET', 'POST'))
@login_required
def summarizer():
    summary = None
    if app.config['NEW_SUM']:
        current = app.config['NEW_SUM'][app.config['CURRENT']]
        summary = dict()
        summary['filename'] = current.case_id
        summary['content'] = current.content
        summary['original'] = current.get_original()
        if current.head:
            summary['indicative'] = current.head.indicative
        summary['informative'] = current.get_informative()
    return render_template('summarizer.html', files=app.config['FILES'],
                           summary=summary, new=app.config['NEW'], threshold=app.config['THRESHOLD'])


@bp.route('/launch_new', methods=('GET', 'POST'))
@login_required
def launch_new():
    app.config['FILES'] = []
    app.config['NEW_SUM'] = []
    app.config['CURRENT'] = 0
    app.config['NEW'] = True
    return redirect(url_for("summarizer.summarizer"))


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if not file.filename:
                flash('لم يتم اختيار أي ملف!')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                cases = tp.get_cases(filename)
                for c in range(len(cases)):
                    case_name = filename + ' ' + str(c)
                    if case_name not in app.config["FILES"]:
                        summary = Summary(cases[c], case_name)
                        app.config["FILES"].append(case_name)
                        app.config["NEW_SUM"].append(summary)
            else:
                flash('الملف غير موجود أو نوعه غير مسموح!')
    return redirect(url_for('summarizer.summarizer'))


@bp.route('/summarize', methods=('GET', 'POST'))
@login_required
def summarize():
    if request.method == 'POST':
        if len(app.config['NEW_SUM']) > 0:
            app.config['THRESHOLD'] = request.form.get("threshold"), request.form.get("unity")
            if request.form.get('content') is not None:
                app.config['NEW_SUM'][app.config["CURRENT"]].set_content(request.form.get('content'))
            app.config['SEPARATORS'] = get_separators()
            for summary in app.config['NEW_SUM']:
                summary.summarize(app.config['SEPARATORS'], app.config['THRESHOLD'])
        else:
            flash('لا يوجد أي محتوى لتلخيصه!')

    return redirect(url_for('summarizer.summarizer'))


@bp.route('/new_summary', methods=('GET', 'POST'))
@login_required
def new_summary():
    if request.method == 'POST':
        try:
            app.config['NEW_SUM'][app.config["CURRENT"]].set_content(request.form.get('content'))
            app.config["CURRENT"] = app.config['FILES'].index(request.form["filename"])
        except:
            pass
    return redirect(url_for('summarizer.summarizer'))


@bp.route('/delete_new', methods=('GET', 'POST'))
@login_required
def delete_new():
    if request.method == 'POST':
        try:
            file = app.config["FILES"][app.config['CURRENT']]
            app.config["NEW_SUM"].pop(app.config['CURRENT'])
            app.config["FILES"].pop(app.config['CURRENT'])
            flash("تم مسح الملف " + '- ' + file + ' -')

            app.config['CURRENT'] -= 1
            if app.config['CURRENT'] < 0:
                app.config['CURRENT'] = 0
        except IndexError:
            flash("لا يوجد أي ملف لمسحه!")

    return redirect(url_for('summarizer.summarizer'))


@bp.route('/save_summaries', methods=('GET', 'POST'))
@login_required
def save_summaries():
    app.config['CURRENT'] = 0
    error = None
    for summary in app.config['NEW_SUM']:
        if summary.head:
            if app.config['NEW']:
                save_summary(summary)
            else:
                update_summary(app.config['id'], summary)
        else:
            error = 'لم يتم تلخيص الملفات بعد!'
            error += '\n' + 'اضغط "تلخيص" ثم "حفظ" أو اضغط "عودة" لإنهاء العملية!'
            break
    if error:
        flash(error)
        return redirect(url_for('summarizer.summarizer'))
    else:
        return redirect(url_for('launcher.launch'))
