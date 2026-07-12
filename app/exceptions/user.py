from app.exceptions.base import DomainError


class UserNotFoundError(DomainError):
    pass


class EmailAlreadyRegisteredError(DomainError):
    pass