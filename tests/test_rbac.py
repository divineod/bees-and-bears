import pytest
from django.urls import reverse
from rest_framework import status

from apps.customers.models import Customer
from tests.factories import (
    CustomerFactory,
    CustomerUserFactory,
    InstallerUserFactory,
    LoanOfferFactory,
)


@pytest.mark.django_db
class TestInstallerPermissions:
    """Test suite for INSTALLER role permissions."""

    def test_installer_can_create_customer(self, installer_client, installer_user):
        url = reverse("customers:customer-create")
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone_number": "+1234567890",
            "address_line1": "456 Oak St",
            "city": "Los Angeles",
            "state": "CA",
            "postal_code": "90001",
            "country": "US",
        }

        response = installer_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Customer.objects.filter(email="jane.smith@example.com").exists()

        customer = Customer.objects.get(email="jane.smith@example.com")
        assert customer.created_by == installer_user

    def test_installer_can_create_loan_offer(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        url = reverse("loans:loanoffer-create")
        data = {
            "customer": customer.id,
            "loan_amount": "15000.00",
            "interest_rate": "6.00",
            "loan_term": 48,
        }

        response = installer_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["loan_amount"] == "15000.00"

    def test_installer_can_view_all_customers(self, installer_client, installer_user):
        CustomerFactory.create_batch(3, created_by=installer_user)
        other_installer = InstallerUserFactory()
        CustomerFactory.create_batch(2, created_by=other_installer)

        url = reverse("customers:customer-list")
        response = installer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 5

    def test_installer_can_view_all_loan_offers(self, installer_client, installer_user):
        customer1 = CustomerFactory(created_by=installer_user)
        LoanOfferFactory.create_batch(2, customer=customer1, created_by=installer_user)

        other_installer = InstallerUserFactory()
        customer2 = CustomerFactory(created_by=other_installer)
        LoanOfferFactory.create_batch(3, customer=customer2, created_by=other_installer)

        url = reverse("loans:loanoffer-list")
        response = installer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 5

    def test_installer_can_view_any_customer_detail(self, installer_client):
        other_installer = InstallerUserFactory()
        customer = CustomerFactory(created_by=other_installer)

        url = reverse("customers:customer-detail", kwargs={"id": customer.id})
        response = installer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(customer.id)

    def test_installer_can_view_any_loan_offer_detail(self, installer_client):
        other_installer = InstallerUserFactory()
        customer = CustomerFactory(created_by=other_installer)
        loan_offer = LoanOfferFactory(customer=customer, created_by=other_installer)

        url = reverse("loans:loanoffer-detail", kwargs={"id": loan_offer.id})
        response = installer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(loan_offer.id)


@pytest.mark.django_db
class TestCustomerPermissions:
    """Test suite for CUSTOMER role permissions."""

    def test_customer_cannot_create_customer(self, customer_client):
        url = reverse("customers:customer-create")
        data = {
            "first_name": "Bob",
            "last_name": "Jones",
            "email": "bob.jones@example.com",
            "phone_number": "+1234567890",
            "address_line1": "789 Pine St",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "country": "US",
        }

        response = customer_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Customer.objects.filter(email="bob.jones@example.com").exists()

    def test_customer_cannot_create_loan_offer(self, customer_client, customer_user):
        installer = InstallerUserFactory()
        customer = CustomerFactory(created_by=installer, user=customer_user)

        url = reverse("loans:loanoffer-create")
        data = {
            "customer": customer.id,
            "loan_amount": "20000.00",
            "interest_rate": "7.00",
            "loan_term": 36,
        }

        response = customer_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_can_view_own_customer_profile(
        self, customer_client, customer_user
    ):
        installer = InstallerUserFactory()
        customer = CustomerFactory(created_by=installer, user=customer_user)

        url = reverse("customers:customer-detail", kwargs={"id": customer.id})
        response = customer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(customer.id)
        assert response.data["email"] == customer.email

    def test_customer_cannot_view_other_customer_profile(
        self, customer_client, customer_user
    ):
        installer = InstallerUserFactory()
        CustomerFactory(created_by=installer, user=customer_user)
        other_customer = CustomerFactory(created_by=installer)

        url = reverse("customers:customer-detail", kwargs={"id": other_customer.id})
        response = customer_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_can_view_own_loan_offers(self, customer_client, customer_user):
        installer = InstallerUserFactory()
        customer = CustomerFactory(created_by=installer, user=customer_user)
        loan_offer = LoanOfferFactory(customer=customer, created_by=installer)

        url = reverse("loans:loanoffer-detail", kwargs={"id": loan_offer.id})
        response = customer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(loan_offer.id)

    def test_customer_cannot_view_other_loan_offers(
        self, customer_client, customer_user
    ):
        installer = InstallerUserFactory()
        CustomerFactory(created_by=installer, user=customer_user)

        other_customer = CustomerFactory(created_by=installer)
        other_loan_offer = LoanOfferFactory(
            customer=other_customer, created_by=installer
        )

        url = reverse("loans:loanoffer-detail", kwargs={"id": other_loan_offer.id})
        response = customer_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_list_shows_only_own_profile(self, customer_client, customer_user):
        installer = InstallerUserFactory()
        my_customer = CustomerFactory(created_by=installer, user=customer_user)

        CustomerFactory.create_batch(3, created_by=installer)

        url = reverse("customers:customer-list")
        response = customer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(my_customer.id)

    def test_customer_loan_offer_list_shows_only_own_offers(
        self, customer_client, customer_user
    ):
        installer = InstallerUserFactory()
        my_customer = CustomerFactory(created_by=installer, user=customer_user)
        LoanOfferFactory.create_batch(2, customer=my_customer, created_by=installer)

        other_customer = CustomerFactory(created_by=installer)
        LoanOfferFactory.create_batch(3, customer=other_customer, created_by=installer)

        url = reverse("loans:loanoffer-list")
        response = customer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2


@pytest.mark.django_db
class TestUnauthenticatedAccess:
    """Test suite for unauthenticated user access."""

    def test_unauthenticated_cannot_create_customer(self, api_client):
        url = reverse("customers:customer-create")
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone_number": "+1234567890",
            "address_line1": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "postal_code": "12345",
            "country": "US",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_create_loan_offer(self, api_client):
        installer = InstallerUserFactory()
        customer = CustomerFactory(created_by=installer)

        url = reverse("loans:loanoffer-create")
        data = {
            "customer": customer.id,
            "loan_amount": "10000.00",
            "interest_rate": "5.00",
            "loan_term": 60,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_view_customer_list(self, api_client):
        url = reverse("customers:customer-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_view_loan_offer_list(self, api_client):
        url = reverse("loans:loanoffer-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_view_customer_detail(self, api_client):
        installer = InstallerUserFactory()
        customer = CustomerFactory(created_by=installer)

        url = reverse("customers:customer-detail", kwargs={"id": customer.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_view_loan_offer_detail(self, api_client):
        installer = InstallerUserFactory()
        customer = CustomerFactory(created_by=installer)
        loan_offer = LoanOfferFactory(customer=customer, created_by=installer)

        url = reverse("loans:loanoffer-detail", kwargs={"id": loan_offer.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRoleProperties:
    """Test suite for User role properties."""

    def test_installer_user_is_installer_property(self):
        installer = InstallerUserFactory()
        assert installer.is_installer is True
        assert installer.is_customer is False

    def test_customer_user_is_customer_property(self):
        customer = CustomerUserFactory()
        assert customer.is_customer is True
        assert customer.is_installer is False

    def test_user_string_representation_includes_role(self):
        installer = InstallerUserFactory(username="john_installer")
        customer = CustomerUserFactory(username="jane_customer")

        assert "Installer" in str(installer)
        assert "john_installer" in str(installer)

        assert "Customer" in str(customer)
        assert "jane_customer" in str(customer)
