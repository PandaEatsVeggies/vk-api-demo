class TooManyRetries(Exception):
    pass


class RequestError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class AccessTokenError(RequestError):
    pass


class TooManyRequestsPerSecondError(RequestError):
    pass


class UserWasDeletedOrBanned(RequestError):
    pass


class ThisProfileIsPrivate(RequestError):
    pass
