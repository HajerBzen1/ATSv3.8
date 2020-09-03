from ATSLegal.FileProcess import remove_useless_characters
from ATSLegal.Process import Functions

ADD = 0.1

SET_ZERO = ['بناء على الم', 'بعد الاطلاع على مجموع أوراق ملف الدعوى', 'بعد الاستماع إلى',
            'في جلستها العلنية المنعقدة']
SET_MORE = ['في الشكل', 'من حيث الشكل', 'في الموضوع', 'من حيث الموضوع', 'شكلا', 'موضوعا', 'قبول', 'رفض']


class Sentence:
    def __init__(self, position: int, content: str):
        self.position = position
        self.content = remove_useless_characters(content)
        self.stems = []
        self.score = 0
        self.included = False

    def set_stems(self, names: list = None):
        from ATSLegal.PreProcess import SectionProcess
        if self.content:
            self.stems = SectionProcess.get_stems(self.content, names)

    def set_score(self, all_words: list, title: str = ''):
        is_zero = False
        for expression in SET_ZERO:
            if expression in self.content:
                is_zero = True
                self.score = 0
                break
        if not is_zero:
            self.score = Functions.get_title_relevance(self.stems, title, all_words)
        for expression in SET_MORE:
            if expression in self.content:
                self.score += ADD
        self.score += Functions.calculate_tf(self.stems, all_words)

    def is_included(self, included):
        self.included = included

    def __repr__(self) -> str:
        return self(self.stems) + '|' + str(self.score)
