class Word:
    def __init__(self, stem: str, occurrence: int):

        self.stem = stem
        self.occurrence = occurrence
        self.tf = 0

    def set_tf(self, total_stems: int):

        self.tf = round(self.occurrence / total_stems, 5)

    def __eq__(self, o: object) -> bool:
        if isinstance(object, Word):
            if object.stem == self.stem:
                return True
        return False

    def __repr__(self) -> str:
        return self.stem + '|' + str(self.occurrence) + '|' + str(self.tf)
