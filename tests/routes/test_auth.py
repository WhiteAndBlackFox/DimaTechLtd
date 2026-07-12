from app.helpers.auth import hash_password
from app.factories import UserFactory


def test_login_success(app, seed):
    seed(UserFactory(email="probe@example.com", hashed_password=hash_password("secret123")))

    _, response = app.test_client.post(
        "/auth/login", json={"email": "probe@example.com", "password": "secret123"}
    )

    assert response.status == 200
    assert "token" in response.json


def test_login_wrong_password(app, seed):
    seed(UserFactory(email="probe@example.com", hashed_password=hash_password("secret123")))

    _, response = app.test_client.post(
        "/auth/login", json={"email": "probe@example.com", "password": "wrong"}
    )

    assert response.status == 401


def test_login_unknown_email(app):
    _, response = app.test_client.post(
        "/auth/login", json={"email": "nobody@example.com", "password": "whatever"}
    )

    assert response.status == 401


def test_login_missing_fields(app):
    _, response = app.test_client.post("/auth/login", json={"email": "probe@example.com"})

    assert response.status == 400