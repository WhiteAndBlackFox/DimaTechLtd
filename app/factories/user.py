import factory

from app.auth import hash_password
from app.models import User, UserRole


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Faker("name")
    hashed_password = factory.LazyFunction(lambda: hash_password("password123"))
    role = UserRole.USER
    is_active = True


class AdminFactory(UserFactory):
    role = UserRole.ADMIN