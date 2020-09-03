from ATSLegal.Entities.Section import Section
from ATSLegal.Entities.Word import Word
from ATSLegal.PreProcess import Segmentation


class Summary:
    def __init__(self, content: str, case_id: str):

        self.case_id = case_id
        self.content = content
        self.head = None
        self.foot = None
        self.body = None  # list
        self.stems = []
        self.total_stems = 0
        self.total_sentences = 0

    def set_content(self, content: str):

        # if the content is changed.
        self.content = content

    def summarize(self, separators: list, threshold: tuple = None):
        self.head, self.foot, self.body = Segmentation.get_sections(self.content, separators)
        self.set_stems(self.foot.names)
        self.set_scores()
        self.set_informative(threshold)

    def set_stems(self, names: list = None):
        stems_l = []
        for section in self.body:
            self.total_sentences += len(section.sentences)
            for sentence in section.sentences:
                sentence.set_stems(names)
                stems_l += sentence.stems

        self.total_stems = len(stems_l)
        stems_d = dict()
        for stem in stems_l:
            if stem in stems_d:
                stems_d[stem] += 1
            else:
                stems_d[stem] = 1

        for stem in stems_d:
            self.stems.append(Word(stem, stems_d[stem]))

    def set_scores(self):

        for stem in self.stems:
            stem.set_tf(self.total_stems)
        for section in self.body:
            for sentence in section.sentences:
                sentence.set_score(self.stems, ' '.join(self.head.indicative['الموضوع']))

    def set_informative(self, threshold: tuple = None):
        for section in self.body:
            section.set_informative(threshold)

    def get_original(self):

        original = dict()
        if self.head:
            original[self.head.section_id] = self.head.get_content()
        if self.body:
            for section in self.body:
                original[section.section_id] = section.get_content()
        if self.foot:
            original[self.foot.section_id] = self.foot.get_content()
        return original

    def get_informative(self):

        informative = dict()
        if self.body:
            for section in self.body:
                informative[section.section_id] = section.get_informative()
        return informative
