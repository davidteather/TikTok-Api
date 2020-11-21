class TikTokCaptchaError(Exception):
    def __init__(
        self,
        message="TikTok blocks this request displaying a Captcha \nTip: Consider using a proxy or a custom_verifyFp as method parameters",
    ):
        self.message = message
        super().__init__(self.message)


class TikTokNotFoundError(Exception):
    def __init__(self, message="The requested object does not exists"):
        self.message = message
        super().__init__(self.message)


class EmptyResponseError(Exception):
    def __init__(self, message="TikTok sent no data back"):
        self.message = message
        super().__init__(self.message)


class JSONDecodeFailure(Exception):
    def __init__(self, message="TikTok sent invalid JSON back"):
        self.message = message
        super().__init__(self.message)
