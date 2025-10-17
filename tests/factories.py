from decimal import Decimal

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.customers.models import Customer
from apps.loans.models import LoanOffer

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user-{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True
    role = User.Role.CUSTOMER


class InstallerUserFactory(UserFactory):
    """Factory for creating User instances with INSTALLER role."""

    username = factory.Sequence(lambda n: f"installer-{n}")
    role = User.Role.INSTALLER


class CustomerUserFactory(UserFactory):
    """Factory for creating User instances with CUSTOMER role."""

    username = factory.Sequence(lambda n: f"customer{n}")
    role = User.Role.CUSTOMER


class CustomerFactory(DjangoModelFactory):
    """Factory for creating Customer instances."""

    class Meta:
        model = Customer

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone_number = factory.Faker("numerify", text="+##########")
    address_line1 = factory.Faker("street_address")
    address_line2 = factory.Faker("secondary_address")
    city = factory.Faker("city")
    state = factory.Faker("state")
    postal_code = factory.Faker("postcode")
    country = "DE"
    created_by = factory.SubFactory(InstallerUserFactory)


class LoanOfferFactory(DjangoModelFactory):
    """Factory for creating LoanOffer instances."""

    class Meta:
        model = LoanOffer

    customer = factory.SubFactory(CustomerFactory)
    loan_amount = Decimal("10000.00")
    interest_rate = Decimal("5.50")
    loan_term = 60
    status = "PENDING"
    created_by = factory.SubFactory(InstallerUserFactory)
