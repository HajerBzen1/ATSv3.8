
from operator import itemgetter

from ATSLegal import FileProcess as tp

NAMES_START = ['والمتركبة من السادة:', 'بحضور السيد:', 'وبمساعدة السيد:']
ROLES = ['رئيس الغرفة رئيسا مقررا', 'رئيس الغرفة رئيسا', 'رئيس الغرفة', "مستشارة مقررة", "مستشارا مقررا", 'مستشارا',
         "مستشارة"]


def get_names(content: str) -> list:

    names = []
    p = content.find(NAMES_START[0]) + len(NAMES_START[0])

    if p >= 0:
        positions = [(p, 0)]
        for role in ROLES:
            q = p
            r = content.find(role, q)
            while r >= 0:
                if r not in [e[0] for e in positions]:
                    positions.append((r, len(role)))
                q = r + len(role)
                r = content.find(role, q)

        positions.sort(key=itemgetter(0), reverse=False)

        for p in range(1, len(positions)):
            start = positions[p - 1][0] + positions[p - 1][1]
            end = positions[p][0]
            names.append(tp.remove_useless_characters(content[start:end]))

        f = content.find(NAMES_START[1])
        f_ = content.find(NAMES_START[2])
        if f >= 0:
            names.append(content[f + len(NAMES_START[1]):content.find('-', f)])
        if f_ >= 0:
            names.append(content[f_ + len(NAMES_START[2]):content.find('-', f_)])

    return names
