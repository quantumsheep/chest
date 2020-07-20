from chest.exceptions.ChestException import ChestException


class InvalidMasterPassword(ChestException):
    def __init__(self):
        super().__init__("Given password doesn't match master password.")
