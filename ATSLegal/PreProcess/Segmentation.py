from operator import itemgetter

from ATSLegal.Entities.Foot import Foot
from ATSLegal.Entities.Head import Head
from ATSLegal import FileProcess as tp



def get_sections(content: str, separators: list = None) -> tuple:
    from ATSLegal.Entities.Section import Section

    head = None
    foot = None
    body = []
    positions = __get_positions(content, separators)  # [(segment_id:int, expression:str, position:int), ...]

    if positions is None:
        return None, None, [Section(0, tp.remove_useless_characters(content))]

    for p in range(len(positions)):
        try:
            end = positions[p + 1][2]
        except:
            end = len(content)
        segment = content[positions[p][2]:end]
        if positions[p][1] == 'ملف رقم':
            head = Head(positions[p][0], tp.remove_useless_characters(segment))
            continue
        if positions[p][1] == 'بذا صدر القرار':
            foot = Foot(positions[p][0], tp.remove_useless_characters(segment))
            continue
        body.append(Section(positions[p][0], tp.remove_useless_characters(segment)))
    return head, foot, body


def __get_positions(content: str, separators: list = None) -> list:
    if separators is None:
        return None

    result = []
    for e in separators:
        p = content.find(e[1])
        if p >= 0:
            result.append(e + (p,))
    result.sort(key=itemgetter(2), reverse=False)
    return result
