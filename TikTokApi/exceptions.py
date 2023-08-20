class TikTokException(Exception):
    """Generic exception that all other TikTok errors are children of."""

    def __init__(self, raw_response, message, error_code=None):
        self.error_code = error_code
        self.raw_response = raw_response
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.error_code} -> {self.message}"


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


class InvalidResponseException(TikTokException):
    """The response from TikTok was invalid."""
