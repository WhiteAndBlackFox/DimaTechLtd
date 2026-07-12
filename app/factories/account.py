import factory

from app.factories.user import UserFactory
from app.models import Account


class AccountFactory(factory.Factory):
    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)
    balance = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)