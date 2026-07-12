from app.exceptions.base import DomainError


class InvalidSignatureError(DomainError):
    pass


class AccountOwnershipError(DomainError):
    pass