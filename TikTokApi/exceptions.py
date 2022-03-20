class TikTokException(Exception):
    """Generic exception that all other TikTok errors are children of."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CaptchaException(TikTokException):
    """TikTok is showing captcha"""


class NotFoundException(TikTokException):
    """TikTok indicated that this object does not exist."""


class EmptyResponseException(TikTokException):
    """TikTok sent back an empty response."""


class SoundRemovedException(TikTokException):
    """This TikTok sound has no id from being removed by TikTok."""


class InvalidJSONException(TikTokException):
    """TikTok returned invalid JSON."""


class NotAvailableException(TikTokException):
    """The requested object is not available in this region."""
