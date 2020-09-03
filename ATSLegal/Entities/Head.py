from ATSLegal.PostProcess import HeadProcess


class Head:
    def __init__(self, section_id: int, content: str):

        self.section_id = section_id
        self.content = content
        self.indicative = None
        if self.content:
            self.set_indicative()

    def set_indicative(self):
        self.indicative = HeadProcess.get_indicative(self.content)
        pass

    def get_content(self):

        result = []
        result_ = self.content.split('\r\n')
        for r in result_:
            result += r.split('\n')
        return [s for s in result if len(s) > 1]
