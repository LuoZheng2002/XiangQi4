class StructureException(BaseException):
    def __init__(self, description):
        self.description = description
