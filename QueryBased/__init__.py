import math
from operator import itemgetter

from ATSLegal.PreProcess.SectionProcess import get_stems


def __get_cos_similarity(q_tmp, s_tmp):
    up = 0
    down_q = 0
    down_s = 0

    for q in q_tmp:
        if q in s_tmp:
            up += q_tmp[q] * s_tmp[q]
        down_q += math.pow(q_tmp[q], 2)

    for s in s_tmp:
        down_s += math.pow(s_tmp[s], 2)

    down = math.sqrt(down_q) * math.sqrt(down_s)
    if down == 0:
        down = 1
    return round(up / down, 5)


def __get_summary(scored_sentences, threshold):
    threshold = math.ceil(threshold * len(scored_sentences))
    scored_sentences.sort(key=itemgetter(2), reverse=True)
    result = sorted(scored_sentences[:threshold], key=itemgetter(0), reverse=False)
    result = ' '.join([r[1] for r in result if r[2] > 0])
    return result


def summarize_query_based(scored_sentences: list, threshold: float = 0.3, query: str = ''):
    # Get stems of all sentences.
    document_stems, sentences_stems = __get_all_stems(scored_sentences)

    # Calculate tf of Query, Q = {s1:tfq1, ..., sn:tfqn}
    q_tmp = __get_query_stems(query)

    result = []
    for s in range(len(sentences_stems)):
        # Get stem tf of each sentence.
        s_tmp = dict()
        for stem in sentences_stems[s]:
            if stem in document_stems:
                if stem not in s_tmp:
                    s_tmp[stem] = document_stems[stem]

        # Calculate cosine similarity (Q, S)
        cos_sim_score = __get_cos_similarity(q_tmp, s_tmp)

        # Calculate sentence score.
        if cos_sim_score > 0:
            sentence_score = scored_sentences[s][1] * cos_sim_score
        else:
            sentence_score = 0
        result.append((s, scored_sentences[s][0], sentence_score))

    # Generate summary.
    summary = __get_summary(result, threshold)

    return summary


def __get_query_stems(query):
    total = 0
    query_stems = get_stems(query)
    q_tmp = dict()
    for q in query_stems:
        if q in q_tmp:
            q_tmp[q] += 1
            total += 1
        else:
            q_tmp[q] = 1
            total += 1
    if total == 0:
        total = 1
    for q in q_tmp:
        q_tmp[q] = round(q_tmp[q] / total, 5)
    return q_tmp


def __get_all_stems(scored_sentences):
    total = 0
    sentences_stems = []
    document_stems = dict()
    for sentence in scored_sentences:
        s_stems = get_stems(sentence[0])
        sentences_stems.append(s_stems)
        for s in s_stems:
            if s in document_stems:
                document_stems[s] += 1
                total += 1
            else:
                document_stems[s] = 1
                total += 1
    if total == 0:
        total = 1
    for s in document_stems:
        document_stems[s] = round(document_stems[s] / total, 5)
    return document_stems, sentences_stems
