class ValidationError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self):
        error_dict = {
            'error': self.message,
            'status_code': self.status_code
        }
        return error_dict