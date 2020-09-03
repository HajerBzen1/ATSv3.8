from ATSLegal.Entities.Word import Word
from ATSLegal.PreProcess import SectionProcess


def calculate_tf(sentence_stems: list, all_words):
    score = 0
    for stem in sentence_stems:
        for word in all_words:
            if isinstance(word, Word) and word.stem == stem:
                score += word.tf
                break
            if isinstance(word, str) and word == stem:
                score += all_words[word]
                break
    return score


def get_title_relevance(sentence_stems: list, title: str, all_words: list):
    title_stems = SectionProcess.get_stems(title)

    down = 0
    for stem in title_stems:
        for word in all_words:
            if word.stem == stem:
                down += word.tf
                break
    if down <= 0:
        down = 1

    up = 0
    for stem in sentence_stems:
        for word in all_words:
            if word.stem == stem and stem in title_stems:
                up += word.tf
                break

    return round(up / down, 5)
