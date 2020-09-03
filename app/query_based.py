from flask import Blueprint, render_template, request, flash

from QueryBased import summarize_query_based
from app.database.operations import select

bp = Blueprint('query_based', __name__)


def get_db_summaries():
    summaries = []
    documents = select('Document', ['id'])
    for d in documents:
        summary = select('Sentence', ['content', 'score'], where_condition='document_id=%s', values=(d[0],),
                         ordered_by='separator_id, position_')
        summaries.append(summary)
    return summaries


@bp.route('/search', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        query = request.form['text']
        query_summaries = []
        if query:
            summaries = get_db_summaries()
            if summaries:
                for summary in summaries:
                    qb_summary = summarize_query_based(summary, threshold=0.1, query=query)
                    query_summaries.append(qb_summary)
            else:
                flash('لا يوجد ملخصات للبحث فيها!')
        else:
            flash('أدخل كلمات البحث!')
        return render_template('query_based.html', summaries=query_summaries, query=query)
    return render_template('query_based.html')
