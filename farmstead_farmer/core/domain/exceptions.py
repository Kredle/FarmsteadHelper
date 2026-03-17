class DomainError(Exception):
    """Base domain/application error."""


class InvalidTokenError(DomainError):
    pass


class UserNotFoundError(DomainError):
    pass


class MissingFieldError(DomainError):
    pass
