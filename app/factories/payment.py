import factory

from app.factories.account import AccountFactory
from app.models import Payment


class PaymentFactory(factory.Factory):
    class Meta:
        model = Payment

    account = factory.SubFactory(AccountFactory)
    user = factory.SelfAttribute("account.user")
    transaction_id = factory.Faker("uuid4")
    amount = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)