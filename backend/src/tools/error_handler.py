class CustomError(Exception):
    def __init__(self, message, origin, status_code):
        self.message = message
        self.origin = origin
        self.status_code = status_code
        super().__init__(self.message)
