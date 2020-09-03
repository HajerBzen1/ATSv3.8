

from ATSLegal.PreProcess import FootProcess


class Foot:
    def __init__(self, section_id: int, content: str):

        self.section_id = section_id
        self.content = content
        self.names = []
        if self.content:
            self.__set_names()

    def __set_names(self):

        self.names = FootProcess.get_names(self.content)

    def get_content(self):

        result = []
        result_ = self.content.split('\r\n')
        for r in result_:
            result += r.split('\n')
        return [s for s in result if len(s) > 1]
