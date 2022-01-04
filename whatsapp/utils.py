from functools import wraps

from whatsapp import errors


def needs_login(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.config.is_logged_in:
            raise errors.NotLoggedInError("Not logged in")
        return func(self, *args, **kwargs)

    return wrapper
