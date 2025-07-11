class ValidationError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class DatabaseInsertError(ValidationError):
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class ResourceNotFoundError(Exception):
    def __init__(self, message, status_code=404):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class ActiveResourceNotFoundError(Exception):
    def __init__(self, message, status_code=404):
        self.message = message
        self.status_code = status_code
        super().__init__(message)