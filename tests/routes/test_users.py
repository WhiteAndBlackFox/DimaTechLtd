from app.factories import AccountFactory, AdminFactory, PaymentFactory, UserFactory
from app.models import UserRole


def test_me_returns_own_profile(app, seed, auth_header):
    user = seed(UserFactory(email="probe@example.com", full_name="Probe User"))

    _, response = app.test_client.get("/users/me", headers=auth_header(user.id, UserRole.USER))

    assert response.status == 200
    assert response.json == {"id": user.id, "email": "probe@example.com", "full_name": "Probe User"}


def test_me_requires_auth(app):
    _, response = app.test_client.get("/users/me")

    assert response.status == 401


def test_me_rejects_admin_role(app, seed, auth_header):
    admin = seed(AdminFactory(email="admin@example.com"))

    _, response = app.test_client.get("/users/me", headers=auth_header(admin.id, UserRole.ADMIN))

    assert response.status == 403


def test_my_accounts_scoped_to_caller(app, seed, auth_header):
    user = seed(UserFactory())
    other = seed(UserFactory())
    seed(AccountFactory(user=user, balance=42))
    seed(AccountFactory(user=other, balance=999))

    _, response = app.test_client.get(
        "/users/me/accounts", headers=auth_header(user.id, UserRole.USER)
    )

    assert response.status == 200
    assert len(response.json) == 1
    assert response.json[0]["balance"] == 42.0


def test_my_payments_scoped_to_caller(app, seed, auth_header):
    user = seed(UserFactory())
    other = seed(UserFactory())
    seed(PaymentFactory(account=AccountFactory(user=user), user=user, amount=10))
    seed(PaymentFactory(account=AccountFactory(user=other), user=other, amount=20))

    _, response = app.test_client.get(
        "/users/me/payments", headers=auth_header(user.id, UserRole.USER)
    )

    assert response.status == 200
    assert len(response.json) == 1
    assert response.json[0]["amount"] == 10.0