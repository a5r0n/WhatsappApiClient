class WhatsappError(Exception):
    pass


class LoginError(WhatsappError):
    pass


class NotLoggedInError(WhatsappError):
    pass


class RequestError(WhatsappError):
    pass
