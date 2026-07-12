from app.factories import AccountFactory, UserFactory
from app.helpers.signature import build_signature


def _payload(account_id, amount, transaction_id, user_id):
    return {
        "transaction_id": transaction_id,
        "user_id": user_id,
        "account_id": account_id,
        "amount": amount,
        "signature": build_signature(account_id, amount, transaction_id, user_id),
    }


def test_credits_existing_account(app, seed):
    user = seed(UserFactory())
    account = seed(AccountFactory(user=user, balance=0))

    _, response = app.test_client.post(
        "/webhook/payment",
        json=_payload(account.id, 150, "tx-existing", user.id),
    )

    assert response.status == 200
    assert response.json == {"status": "ok"}


def test_creates_account_when_missing(app, seed):
    user = seed(UserFactory())

    _, response = app.test_client.post(
        "/webhook/payment",
        json=_payload(999999, 50, "tx-new-account", user.id),
    )

    assert response.status == 200
    assert response.json == {"status": "ok"}


def test_duplicate_transaction_id_is_not_double_credited(app, seed):
    user = seed(UserFactory())
    account = seed(AccountFactory(user=user, balance=0))
    payload = _payload(account.id, 100, "tx-dup", user.id)

    _, first = app.test_client.post("/webhook/payment", json=payload)
    _, second = app.test_client.post("/webhook/payment", json=payload)

    assert first.status == 200
    assert second.status == 200
    assert second.json == {"status": "already processed"}


def test_invalid_signature_is_rejected(app, seed):
    user = seed(UserFactory())

    _, response = app.test_client.post(
        "/webhook/payment",
        json={
            "transaction_id": "tx-bad-sig",
            "user_id": user.id,
            "account_id": 1,
            "amount": 10,
            "signature": "not-a-real-signature",
        },
    )

    assert response.status == 400


def test_unknown_user_returns_404(app):
    _, response = app.test_client.post(
        "/webhook/payment",
        json=_payload(1, 10, "tx-unknown-user", 999999),
    )

    assert response.status == 404


def test_account_belonging_to_another_user_is_rejected(app, seed):
    owner = seed(UserFactory())
    intruder = seed(UserFactory())
    account = seed(AccountFactory(user=owner, balance=0))

    _, response = app.test_client.post(
        "/webhook/payment",
        json=_payload(account.id, 10, "tx-wrong-owner", intruder.id),
    )

    assert response.status == 400