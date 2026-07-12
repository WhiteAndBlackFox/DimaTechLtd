from app.factories import AccountFactory, AdminFactory, UserFactory
from app.models import UserRole


def test_me_returns_own_profile(app, seed, auth_header):
    admin = seed(AdminFactory(email="admin@example.com", full_name="Root Admin"))

    _, response = app.test_client.get("/admin/me", headers=auth_header(admin.id, UserRole.ADMIN))

    assert response.status == 200
    assert response.json == {"id": admin.id, "email": "admin@example.com", "full_name": "Root Admin"}


def test_me_requires_auth(app):
    _, response = app.test_client.get("/admin/me")

    assert response.status == 401


def test_me_rejects_user_role(app, seed, auth_header):
    user = seed(UserFactory())

    _, response = app.test_client.get("/admin/me", headers=auth_header(user.id, UserRole.USER))

    assert response.status == 403


def test_list_users_includes_accounts(app, seed, auth_header):
    admin = seed(AdminFactory())
    user = seed(UserFactory())
    seed(AccountFactory(user=user, balance=15))

    _, response = app.test_client.get("/admin/users", headers=auth_header(admin.id, UserRole.ADMIN))

    assert response.status == 200
    by_id = {row["id"]: row for row in response.json}
    assert by_id[user.id]["accounts"][0]["balance"] == 15.0


def test_create_user(app, seed, auth_header):
    admin = seed(AdminFactory())

    _, response = app.test_client.post(
        "/admin/users",
        headers=auth_header(admin.id, UserRole.ADMIN),
        json={"email": "new@example.com", "full_name": "New Guy", "password": "pass1234"},
    )

    assert response.status == 201
    assert response.json["email"] == "new@example.com"


def test_create_user_duplicate_email_conflict(app, seed, auth_header):
    admin = seed(AdminFactory())
    seed(UserFactory(email="dup@example.com"))

    _, response = app.test_client.post(
        "/admin/users",
        headers=auth_header(admin.id, UserRole.ADMIN),
        json={"email": "dup@example.com", "full_name": "Dup", "password": "pass1234"},
    )

    assert response.status == 409


def test_update_user(app, seed, auth_header):
    admin = seed(AdminFactory())
    user = seed(UserFactory(full_name="Old Name"))

    _, response = app.test_client.put(
        f"/admin/users/{user.id}",
        headers=auth_header(admin.id, UserRole.ADMIN),
        json={"full_name": "New Name"},
    )

    assert response.status == 200
    assert response.json["full_name"] == "New Name"


def test_update_user_not_found(app, seed, auth_header):
    admin = seed(AdminFactory())

    _, response = app.test_client.put(
        "/admin/users/999999",
        headers=auth_header(admin.id, UserRole.ADMIN),
        json={"full_name": "Nobody"},
    )

    assert response.status == 404


def test_delete_user(app, seed, auth_header):
    admin = seed(AdminFactory())
    user = seed(UserFactory())

    _, response = app.test_client.delete(
        f"/admin/users/{user.id}", headers=auth_header(admin.id, UserRole.ADMIN)
    )

    assert response.status == 204


def test_delete_user_not_found(app, seed, auth_header):
    admin = seed(AdminFactory())

    _, response = app.test_client.delete(
        "/admin/users/999999", headers=auth_header(admin.id, UserRole.ADMIN)
    )

    assert response.status == 404


def test_admin_routes_reject_user_role(app, seed, auth_header):
    user = seed(UserFactory())

    _, response = app.test_client.get("/admin/users", headers=auth_header(user.id, UserRole.USER))

    assert response.status == 403