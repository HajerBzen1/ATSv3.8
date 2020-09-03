import re

from nltk import ISRIStemmer
from pyarabic import araby

from ATSLegal.Entities.Sentence import Sentence
from ATSLegal.Entities.Word import Word
from ATSLegal.PreProcess.Constantes import WILAYAS, DAYS, MONTHS, STOPWORDS

NAMES_START = ['الأستاذ', 'السيد']
NAMES_END = ['المحام', 'المعتمد', 'محضر', 'لدى']

PATTERN_1 = '\(\w.\w\)|\(\w\)'
PATTERN_2 = ['\s*(بن عبد\s\w+)', '\s*(عبد\s+\w+)', '\s*(بن\s\w+)', '\s*(\w+\s+\w+)']
PATTERN_3 = [NAMES_START[0] + '\w*' + '\s+([\w+\s+]+)[.،]*',
             NAMES_START[0] + '[ة]' + '*\s+([\w+\s+]+)' + NAMES_END[0],
             NAMES_START[0] + '[ة]' + '*\s+([\w+\s+]+)' + NAMES_END[1],
             NAMES_START[1] + '[ة]' + '*\s+([\w+\s+]+)' + NAMES_END[2],
             NAMES_START[0] + '[ة]' + '*\s+([\w+\s+]+)' + NAMES_END[3]]


def get_sentences(content: str) -> list:
    """
    The method splits the segment into sentences.
    """

    def replace(matchobj):
        group = matchobj.group(0)
        if group[0] == ' ' and group[1].isalpha() and group[-1] == ' ' and group[-2].isalpha():
            return group
        return group[:3] + '\n' + group[4:]

    paragraphs = re.split(r'\.\r*\n+', content)
    sentences = []
    i = 0
    result = []
    for p in paragraphs:
        re.sub(r'.{2}\. .{2}', replace, p)
        result += p.split('.\n')
    for s in result:
        if len(s) > 1:
            sentences.append(Sentence(i, s))
            i += 1
    return sentences


def get_stems(text: str, names=None) -> list:
    if names is None:
        names = []

    stems = __get_names(text, names)
    # remove names
    for n in names:
        text = re.sub(n, ' ', text)

    for w in WILAYAS:
        stems += re.findall(w, text)
        text = re.sub(w, ' ', text)



    # Tokenizing.
    tokens = __get_tokens(text)

    # Stemming.
    ps = ISRIStemmer()
    for t in tokens:
        if len(t) > 0:
            if t not in DAYS + MONTHS:
                # Normalisation.
                t = re.sub(r'أ' + r'|' + r'إ' + r'|' + r'آ', 'ا', t)
                t = re.sub(r'ي', 'ى', t)
                t = re.sub(r'ة', 'ه', t)

                t = ps.stem(t)
            stems.append(t)
    return stems


def __get_names(text: str, names=None) -> list:
    """
    The method retrieves proper names including names mentioned in foot segment.
    """
    if names is None:
        names = []

    entities = []
    for name in names:
        entities += re.findall(name, text)
        text = re.sub(name, ' ', text)
    entities += re.findall(PATTERN_1, text)
    text = re.sub(PATTERN_1, ' ', text)
    entities += re.findall(PATTERN_3[1], text)
    text = re.sub(PATTERN_3[1], ' ', text)
    entities += re.findall(PATTERN_3[2], text)
    text = re.sub(PATTERN_3[2], ' ', text)
    entities += re.findall(PATTERN_3[3], text)
    text = re.sub(PATTERN_3[3], ' ', text)
    entities += re.findall(PATTERN_3[4], text)
    text = re.sub(PATTERN_3[4], ' ', text)

    two_names_min = re.findall(PATTERN_3[0], text)
    for element in two_names_min:
        if len(element) > 3:
            list_ = element.split(' ')
            n = 0
            name = ''
            for i in range(2):
                if len(list_) > n:
                    if list_[n] == "بن":
                        name += list_[n] + ' '
                        if list_[n + 1] == "عبد":
                            name += list_[n + 1] + ' ' + list_[n + 2] + ' ' * abs(i - 1)
                            n = n + 3
                        else:
                            name += list_[n + 1]
                            n = n + 2
                    elif list_[n] == "عبد":
                        name += list_[n] + ' ' + list_[n + 1] + ' ' * abs(i - 1)
                        n = n + 2
                    else:
                        name += list_[n] + ' ' * abs(i - 1)
                        n = n + 1
        else:
            name = element
        entities.append(name)
    return entities


def __get_tokens(text: str) -> list:
    """
    The method splits the segment into words.
    It removes any stopwords and not alpha words.
    :param text: string
    :return: list of string
    """
    tokens = araby.tokenize(text)
    e = 0
    while e < len(tokens):
        if not tokens[e].isalpha() or tokens[e] in STOPWORDS or len(tokens[e]) <= 1:
            tokens.pop(e)
        else:
            e += 1
    return tokens


def word_exists(stem: str, all_words: list) -> Word:
    for word in all_words:
        if word.stem == stem:
            return word
