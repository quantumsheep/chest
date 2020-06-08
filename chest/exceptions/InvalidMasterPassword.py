class InvalidMasterPassword(Exception):
    def __init__(self):
        self.message = "Given password doesn't match master password."
