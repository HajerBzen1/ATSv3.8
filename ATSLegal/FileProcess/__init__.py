import os
import re

from pdfReader.pdf_reader import PDFReader

UPLOAD_FOLDER = os.getcwd() + '/app/tmp/'


def remove_useless_characters(text: str) -> str:
    if len(text) > 0:
        # remove useless characters in the beginning of the text.
        text = list(text)
        c = 0
        while c < len(text):
            if text[c] in ["\n", "\r", " "]:
                text[c] = ""
                c += 1
            else:
                break
        # remove useless characters in the end of the text.
        c = len(text) - 1
        while c > 0:
            if text[c] in ["\n", "\r", " "]:
                text[c] = ""
                c -= 1
            else:
                break
        return ''.join(text)
    return text


def get_content(filename: str) -> str:
    extension = filename.split(".")[-1]
    content = []
    path = UPLOAD_FOLDER + filename
    if os.path.exists(path):
        if extension == "txt":
            f = open(path, 'rb')
            content = f.read().decode()
            f.close()
        elif extension == "pdf":
            content = PDFReader(path).text
        else:
            print("نوع الملف غير مسموح")
        if not content:
            print("لا يوجد محتوى في الملف " + filename)
        os.remove(path)
    else:
        print("الملف غير موجود!")
    return content


def remove_head_foot(text):
    # remove page number, header and footer of a page.
    p_page_number = re.compile(r'\n\d+\n')
    p_foot = re.compile(r'\n' + r'مجلة المحكمة العليا -العدد' + r'.*?\n')
    p_head = re.compile(r'\n' + r'.*?' + r'ملف رقم ' + r'\d+\n')
    for i in range(2):
        text = p_page_number.sub('\n', text)
        text = p_foot.sub('\n', text)
        text = p_head.sub('\n', text)
    # remove the very first page number.
    p = text.find('\n')
    if text[:p].isnumeric():
        text = text[p + 1:]
    return text


def remove_tachkil(text):
    tachkil = ['َ', 'ً', 'ُ', 'ٌ', 'ِ', 'ٍ', 'ّ', 'ْ', 'ـ']
    result = ''
    for c in text:
        if c not in tachkil:
            result += c
    return result


def modify(text):
    def replace(matchobj):
        group = matchobj.group(0)
        if group[0] == ' ':
            group = group[1:]
        if group[-1] not in [' ', ':', '،', '؛', '.']:
            group = group[:-1] + ' ' + group[-1]
        return group

    pattern = re.compile(r'.[:،؛\.].*?', re.DOTALL)
    return pattern.sub(replace, text)


def remove_multi_spaces(text):
    def replace(matchobj):
        if ' ' in matchobj.group(0):
            return ' '
        return matchobj.group(0)

    return re.sub(r' +', replace, text)


def process_text(text):
    text = remove_head_foot(text)
    text = remove_tachkil(text)
    text = modify(text)
    text = remove_multi_spaces(text)
    return text


def remove_useless_newline(text):
    start = text.find('الموضوع:')
    end = text.find('المتركبة من السادة:') + len('المتركبة من السادة:')
    body = text[start: end]
    body = re.sub(r'\. \n', '.\n', body)

    def replace(matchobj):
        if matchobj.group(0)[0] != '.':
            return matchobj.group(0)[0] + ' '

    body = re.sub(r'[^\.]\n', replace, body)
    return text[:start] + body + text[end:]


def get_cases(filename: str) -> list:
    content = process_text(get_content(filename))
    cases = []
    pattern = re.compile(r"ملف رقم " + r".+?" + r"قرار بتاريخ " + r'\d+/\d+/\d+')
    pattern_end = re.compile(r'بمساعدة السيد' + r'.*?' + 'أمين الضبط.')
    try:
        p = pattern.search(content).start()
        q = pattern_end.search(content, p).start()
    except:
        p = -1
        q = -1
    while p >= 0 and q >= 0:
        cases.append(remove_useless_newline(content[p:content.find('\n', q + 1)]))
        try:
            p = pattern.search(content, q).start()
            q = pattern_end.search(content, p).start()
        except:
            p = -1
            q = -1
    return cases
