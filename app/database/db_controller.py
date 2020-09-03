from ATSLegal.Entities.Summary import Summary
from app.database.operations import select, insert, delete, update


def get_separators():
    result = select('Separator', '*', ordered_by='id')
    return result


def __save_indicative(indicative: dict) -> int:
    # save indicative
    d_columns = ['file_number', 'decision_date', 'subject', 'principle']
    p_columns = ['document_id', 'party_name']
    l_columns = ['document_id', 'text']

    d_values = (indicative['ملف رقم'][0], indicative['قرار بتاريخ'][0],
                indicative['الموضوع'][0], indicative['المبدأ'][0])
    d_id = insert('Document', d_columns, d_values)

    for party in indicative['أطراف القضية']:
        p_values = (d_id, party)
        insert('Party', p_columns, p_values)

    for law in indicative['نصوص قانونية']:
        l_values = (d_id, law)
        insert('Legal_Text', l_columns, l_values)

    return d_id


def __save_sections(document_id, summary):
    s_columns = ['document_id', 'Separator_id', 'position_', 'content', 'score', 'included']
    # save head
    sentences = summary.head.get_content()
    for s in range(len(sentences)):
        s_values = (document_id, summary.head.section_id, s, sentences[s], 0, False)
        insert('Sentence', s_columns, s_values)

    # save body
    for section in summary.body:
        for sentence in section.sentences:
            s_values = (document_id, section.section_id, sentence.position,
                        sentence.content, sentence.score, sentence.included)
            insert('Sentence', s_columns, s_values)

    # save foot
    sentences = summary.foot.get_content()
    for s in range(len(sentences)):
        s_values = (document_id, summary.foot.section_id, s, sentences[s], 0, False)
        insert('Sentence', s_columns, s_values)


def save_summary(summary: Summary):
    document_id = __save_indicative(summary.head.indicative)
    __save_sections(document_id, summary)


def get_stored_summaries():
    stored = []
    cases = []
    documents = select('Document', '*', ordered_by='file_number')
    for d in documents:
        summary = dict()
        summary["id"] = d[0]
        summary['filename'] = d[1]
        summary['indicative'] = __get_stored_indicative(d)

        summary['original'], summary['informative'] = __get_section(d[0])
        stored.append(summary)
        cases.append(summary['filename'])
    return cases, stored


def __get_section(document_id):
    original = dict()
    informative = dict()
    separators = [s[0] for s in select('Separator', '*', ordered_by='id')]
    for s_id in separators:
        sentences = select('Sentence', '*',
                           where_condition='document_id=%s AND separator_id=%s',
                           values=(document_id, s_id), ordered_by='position_')
        original[s_id] = [s[4] for s in sentences]
        informative[s_id] = [s[4] for s in sentences if s[6] == 'true']

    return original, informative


def __get_stored_indicative(document):
    indicative = dict()
    indicative['ملف رقم'] = [document[1]]
    indicative['قرار بتاريخ'] = [document[2]]
    parties = select('Party', '*', where_condition='document_id=%s',
                     values=(document[0],), ordered_by='id')
    indicative['أطراف القضية'] = [p[2] for p in parties]
    indicative['الموضوع'] = [document[3]]
    laws = select('Legal_Text', '*', where_condition='document_id=%s',
                  values=(document[0],), ordered_by='id')
    indicative['نصوص قانونية'] = [l[2] for l in laws]
    indicative['المبدأ'] = [document[4]]
    return indicative


def delete_summary(id_):
    delete("Document", ["id"], (id_,))


def __update_indicative(document_id, indicative):
    # save indicative
    d_columns = ['file_number', 'decision_date', 'subject', 'principle']
    p_columns = ['party_name']
    l_columns = ['text']

    d_values = (indicative['ملف رقم'][0], indicative['قرار بتاريخ'][0],
                indicative['الموضوع'][0], indicative['المبدأ'][0])
    d_id = update('Document', d_columns, d_values, where_columns=['id'], where_values=(document_id,))

    for party in indicative['أطراف القضية']:
        p_values = (party,)
        update('Party', p_columns, p_values, where_columns=['document_id'], where_values=(document_id,))

    for law in indicative['نصوص قانونية']:
        l_values = (law,)
        update('Legal_Text', l_columns, l_values, where_columns=['document_id'], where_values=(document_id,))


def __update_sections(document_id, summary):
    s_columns = ['Separator_id', 'position_', 'content', 'score', 'included']
    # save head
    sentences = summary.head.get_content()
    for s in range(len(sentences)):
        s_values = (summary.head.section_id, s, sentences[s], 0, False)
        update('Sentence', s_columns, s_values, where_columns=['document_id'], where_values=(document_id,))

    # save body
    for section in summary.body:
        for sentence in section.sentences:
            s_values = (section.section_id, sentence.position,
                        sentence.content, sentence.score, sentence.included)
            update('Sentence', s_columns, s_values, where_columns=['document_id'], where_values=(document_id,))

    # save foot
    sentences = summary.foot.get_content()
    for s in range(len(sentences)):
        s_values = (summary.foot.section_id, s, sentences[s], 0, False)
        update('Sentence', s_columns, s_values, where_columns=['document_id'], where_values=(document_id,))


def update_summary(document_id, summary):
    __update_indicative(document_id, summary.head.indicative)
    __update_sections(document_id, summary)
