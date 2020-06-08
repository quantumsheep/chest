class InitializationNeeded(Exception):
    def __init__(self):
        self.message = "An initialization is needed."
