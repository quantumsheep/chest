from chest.exceptions.ChestException import ChestException


class ValueNotStored(ChestException):
    def __init__(self, name: str):
        super().__init__(f"No value named '{name}' is currently stored.")
