import hashlib
from decimal import Decimal

from config import SECRET_KEY


def build_signature(account_id: int, amount: int | float | Decimal, transaction_id: str, user_id: int) -> str:
    raw = f"{account_id}{amount}{transaction_id}{user_id}{SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_signature(
    account_id: int, amount: int | float | Decimal, transaction_id: str, user_id: int, signature: str
) -> bool:
    return build_signature(account_id, amount, transaction_id, user_id) == signature