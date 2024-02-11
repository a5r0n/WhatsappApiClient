from functools import wraps
import aiohttp
from aioretry import RetryInfo, RetryPolicyStrategy, retry
from loguru import logger
from whatsapp import errors

__all__ = [
    "needs_login",
    "retry_logger_factory",
    "retry_policy",
    "retry",
]


def needs_login(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.config.is_logged_in:
            raise errors.NotLoggedInError("Not logged in")
        return func(self, *args, **kwargs)

    return wrapper


def retry_logger_factory(log: str, **kwargs):
    def _retry_logger(info: RetryInfo):
        logger.bind(
            error=info.exception,
            error_args=info.exception.args,
            info_retry=info.fails,
            info_since=info.since,
            **kwargs,
        ).warning(
            log,
            info.fails,
            info.exception,
        )

    return _retry_logger


def retry_policy(info: RetryInfo) -> RetryPolicyStrategy:
    if info.fails > 3:
        return True, 0

    code = isinstance(info.exception, errors.RequestError) and info.exception.status
    code = code or (
        isinstance(info.exception, aiohttp.ClientResponseError)
        and info.exception.status
    )

    if code:
        if code == 401:
            # 401 is unauthorized, so we should stop retrying
            return True, 0
        elif code == 403:
            # 403 is forbidden, so we should stop retrying
            return True, 0
        elif code == 429:
            # 429 is too many requests, so we should retry
            pass

    if isinstance(info.exception, errors.CloudAPIError):
        if info.exception.error_code == 131056:  # pair rate limit hit
            return (
                False,
                info.fails**1.5,
            )  # retry with exponential backoff, 1s, 2.8s, 5.19s

    return False, info.fails + 1**1.5  # retry with exponential backoff, 2.8s, 5.19s, 8s
