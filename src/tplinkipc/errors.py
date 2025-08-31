class ApiError(Exception):
    """Base class for TPLink IPC API errors."""
    pass

class LoginError(ApiError):
    """Raised when login to the TPLink IPC API fails."""
    def __init__(self, message: str):
        super().__init__(message)

class SessionExpiredError(ApiError):
    """Raised when the TPLink IPC API session has expired."""
    def __init__(self, message: str):
        super().__init__(message)

class ConnectionError(ApiError):
    """Raised when there is a connection error with the TPLink IPC API."""
    def __init__(self, message: str):
        super().__init__(message)