import math


def get_threshold(threshold: tuple = None, total: int = 0) -> int:
    if threshold and len(threshold) > 1:
        if threshold[1] == '%':
            return math.ceil((int(threshold[0]) / 100) * total)
        if threshold[1] == 'جملة':
            return int(threshold[0])
    return math.ceil(0.3 * total)


def get_summary(sentences: list, threshold: int):
    informative = sorted(sentences, key=lambda sentence: sentence.score, reverse=True)[:threshold]
    for sentence in informative:
        sentence.is_included(True)
