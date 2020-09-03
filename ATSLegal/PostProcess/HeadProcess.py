import re
from operator import itemgetter

from ATSLegal import FileProcess as tp

INFO_START = ['ملف رقم', 'قرار بتاريخ', 'قضية ', 'الموضوع', 'الموسوع', 'المبدأ', 'المبد أ']
PARTIES = ['ضد ', 'بحضور ', 'قضية']
NUMBER_WORD = ' رقم:'
NEWSPAPER_START = 'جريدة رسمية عدد:'

LAWS_START = ['قانون', 'أمر', 'مرسوم', 'نظام', 'مرسوم تنفيذي']
ARTICLE_INCLUDE = ['مكرر', 'الأولى', 'فقرة أخيرة']
ARTICLE_START = ["المادة", "المادتان", "المواد"]


def get_indicative(content: str) -> dict:
    positions = __get_start_positions(content)
    head_info = dict()
    for law in range(len(positions) - 1):
        p = positions[law]
        q = positions[law + 1]
        if p[0] == 'ملف رقم':
            head_info['ملف رقم'] = __get_number(content[p[1]:q[1]])
            continue
        if p[0] == 'قرار بتاريخ':
            head_info['قرار بتاريخ'] = __get_date(content[p[1]:q[1]])
            continue
        if p[0] == 'قضية ':
            head_info['أطراف القضية'] = __get_parties(content[p[1]:q[1]])
            continue
        if p[0] == 'الموضوع' or p[0] == 'الموسوع':
            head_info[INFO_START[3]] = __get_subject(content[p[1]:q[1]])
            continue
        if p[0] == 'نصوص قانونية':
            head_info['نصوص قانونية'] = __get_laws_2(content[p[1]:q[1]])
            continue
        if p[0] == 'المبدأ' or p[0] == 'المبد أ':
            head_info['المبدأ'] = __get_principle(content[p[1]:q[1]])
            continue

    if 'ملف رقم' not in head_info:
        head_info['ملف رقم'] = [' ']
    if 'قرار بتاريخ' not in head_info:
        head_info['قرار بتاريخ'] = [' ']
    if 'أطراف القضية' not in head_info:
        head_info['أطراف القضية'] = [' ']
    if 'الموضوع' not in head_info:
        head_info[INFO_START[3]] = [' ']
    if 'نصوص قانونية' not in head_info:
        head_info['نصوص قانونية'] = [' ']
    if 'المبدأ' not in head_info:
        head_info['المبدأ'] = [' ']
    return head_info


def __get_start_positions(content: str) -> list:
    positions = []
    for s in INFO_START:
        p = content.find(s)
        if p >= 0:
            positions.append((s, p))

    p = __get_laws_start(content)
    if p >= 0:
        positions.append(('نصوص قانونية', p))
    positions.append(('end', len(content)))
    positions.sort(key=itemgetter(1), reverse=False)
    return positions


def __get_laws_start(content):
    laws_p = len(content)
    for i in range(0, len(LAWS_START)):
        item = content.find(LAWS_START[i] + NUMBER_WORD)
        if 0 <= item <= laws_p:
            laws_p = item
    return laws_p


def __get_number(info):
    """
    The method retrieves the number of the document.
    :return:string
    """
    return re.findall(INFO_START[0] + r'\s(\d+)', info)


def __get_date(info):
    """
    The method retrieves the date of the document.
    :return: string
    """

    return re.findall(INFO_START[1] + r'\s(\d+\s*/\d+\s*/\d+)', info)


def __get_parties(info):
    """
    The method retrieves the parties of the document.
    :return:list of string
    """
    positions = []
    for party in PARTIES:
        p = info.find(party)
        if p >= 0:
            positions.append(p)
    positions.sort()

    parties = []
    for p in range(len(positions) - 1):
        parties.append(tp.remove_useless_characters(info[positions[p]:positions[p + 1]]))
    parties.append(tp.remove_useless_characters(info[positions[-1]:len(info)]))
    return parties


def __get_subject(info):
    """
    The method retrieves the subject of the document.
    :return: string
    """
    if info.find(INFO_START[3] + ":") >= 0:
        subject = info[info.find(INFO_START[3] + ":") + len(INFO_START[3] + ":"):]
        return [tp.remove_useless_characters(subject)]
    elif info.find(INFO_START[4] + ":") >= 0:
        subject = info[info.find(INFO_START[4] + ":") + len(INFO_START[4] + ":"):]
        return [tp.remove_useless_characters(subject)]
    else:
        return [' ']


def __get_laws(info):
    """
    The method retrieves the laws mentioned in the head of the document.
    :return: list of dictionary, each dict is a law with its details.
    """

    re_law_num = re.compile(r'\d+\s*-\s*\d+')
    re_law_article = re.compile(r'\d+\s*' + ARTICLE_INCLUDE[0] + r'/*\d*|\d+\/\d+|\d+\s*'
                                + ARTICLE_INCLUDE[2] + r'|\d+|' + ARTICLE_INCLUDE[1])

    laws_list = []
    for i in range(len(LAWS_START)):
        law = LAWS_START[i]
        p = 0
        law_p = p

        # the number of the law and the code name
        while law_p >= 0:
            law_p = info.find(law + NUMBER_WORD, p)
            if law_p - 1 > 0 and info[law_p - 1] == 'ل':
                law_p = -1
            if law_p >= 0:
                law_dict = dict()
                p = law_p + len(law + NUMBER_WORD)
                law_num = re_law_num.findall(info)[0]
                law_dict[LAWS_START[i] + ' رقم'] = law_num
                law_code = info[info.find('(', p) + 1: info.find(')،', p)]
                law_dict['من '] = law_code

                # the set of articles numbers
                for a in ARTICLE_START:
                    article_p = info.find(a, p)
                    if article_p >= 0:
                        p = article_p + len(a)
                        articles = re_law_article.findall(info[article_p:info.find('،', article_p)])
                        law_dict[a] = articles
                        break

                # the number of the official newspaper.
                journal_p = info.find(NEWSPAPER_START, p)
                if journal_p >= 0:
                    p = journal_p + len(NEWSPAPER_START)
                    journal = info[p:info.find('.', p)]
                    journal_num = re.findall(r'\d+', journal)[0]
                    law_dict[NEWSPAPER_START] = journal_num

                laws_list.append(law_dict)
    return laws_list


def __get_principle(info):
    """
    The method retrieves the principle of the document.
    :return: string
    """
    if info.find(INFO_START[5] + ":") >= 0:
        principle = info[info.find(INFO_START[5] + ":") + len(INFO_START[5] + ":"):]
        return [tp.remove_useless_characters(principle)]
    elif info.find(INFO_START[6] + ":") >= 0:
        principle = info[info.find(INFO_START[5] + ":") + len(INFO_START[6] + ":"):]
        return [tp.remove_useless_characters(principle)]
    else:
        return [' ']


def __get_laws_2(info):
    positions = []
    for e in LAWS_START:
        p = info.find(e + NUMBER_WORD)
        while p >= 0:
            if p == 0 or (p > 0 and info[p - 1] != 'ل'):
                positions.append(p)
            p = info.find(e + NUMBER_WORD, p + 1)
    positions.append(len(info))

    positions.sort()
    head_info = []
    for p in range(len(positions) - 1):
        head_info.append(info[positions[p]:positions[p + 1]])
    return head_info
