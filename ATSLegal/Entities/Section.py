from ATSLegal.PostProcess.SectionProcess import get_threshold, get_summary
from ATSLegal.PreProcess import SectionProcess


class Section:
    def __init__(self, section_id: int, content: str):

        self.section_id = section_id
        self.content = content
        self.sentences = []
        if self.content:
            self.__set_sentences()

    def __set_sentences(self):

        self.sentences = SectionProcess.get_sentences(self.content)

    def set_informative(self, threshold: tuple = None):
        threshold = get_threshold(threshold, len(self.sentences))
        get_summary(self.sentences, threshold)

    def get_content(self) -> list:

        sentences = []
        for sentence in self.sentences:
            sentences.append(sentence.content + '.')
        return sentences

    def get_informative(self) -> list:

        sentences = []
        for sentence in self.sentences:
            if sentence.included:
                sentences.append(sentence.content + '. ')
        return sentences
