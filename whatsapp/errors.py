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


class CloudAPIError(WhatsappError):
    def __init__(self, status: int, reason: str, message: str, data: Any):
        self.status = status
        self.reason = reason
        self.message = message
        self.data = data

        if isinstance(data, dict):
            self.error_code = data.get("code", -1)
        else:
            self.error_code = -1
