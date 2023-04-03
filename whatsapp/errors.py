from typing import Any


class WhatsappError(Exception):
    pass


class LoginError(WhatsappError):
    pass


class NotLoggedInError(WhatsappError):
    pass


class RequestError(WhatsappError):
    def __init__(self, status: int, reason: str, message: str, data: Any):
        self.status = status
        self.reason = reason
        self.message = message
        self.data = data
