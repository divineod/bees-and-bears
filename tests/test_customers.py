import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from apps.customers.models import Customer
from tests.factories import CustomerFactory


def get_customer_test_data(endpoint, customer_id=None, **kwargs):
    """
    Helper function to get URL and data for customer endpoints.

    Args:
        endpoint: The endpoint name ('create', 'detail', 'list')
        customer_id: The customer ID for detail endpoint
        **kwargs: Override default values for any field

    Returns:
        tuple: (url, data) for the test
    """
    urls = {
        "create": reverse("customers:customer-create"),
        "list": reverse("customers:customer-list"),
    }

    if endpoint == "detail" and customer_id is not None:
        urls["detail"] = reverse(
            "customers:customer-detail", kwargs={"id": customer_id}
        )

    default_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        "address_line1": "123 Main St",
        "address_line2": "Apt 4B",
        "city": "Berlin",
        "state": "Berlin",
        "postal_code": "10405",
        "country": "DE",
    }

    url = urls.get(endpoint)
    data = {**default_data, **kwargs} if endpoint in ["create"] else None

    return url, data


@pytest.mark.django_db
class TestCreateCustomer:
    """Test suite for customer creation endpoint."""

    def test_create_customer_success(self, installer_client, installer_user):
        url, data = get_customer_test_data("create")

        response = installer_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["first_name"] == "John"
        assert response.data["last_name"] == "Doe"
        assert response.data["email"] == "john.doe@example.com"
        assert response.data["full_name"] == "John Doe"
        assert Customer.objects.filter(email="john.doe@example.com").exists()

        customer = Customer.objects.get(email="john.doe@example.com")
        assert customer.created_by == installer_user

    def test_create_customer_unauthenticated(self, api_client):
        url, data = get_customer_test_data("create")

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_customer_duplicate_email(self, installer_client, installer_user):
        CustomerFactory(email="existing@example.com", created_by=installer_user)
        url, data = get_customer_test_data("create", email="existing@example.com")

        response = installer_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    @pytest.mark.parametrize(
        "data_overrides,expected_error_field",
        [
            (
                {
                    "first_name": "John",
                    "last_name": None,
                    "email": None,
                    "address_line1": None,
                },
                None,
            ),
            ({"email": "invalid-email"}, "email"),
        ],
        ids=["missing_required_fields", "invalid_email_format"],
    )
    def test_create_customer_validation_errors(
        self, installer_client, data_overrides, expected_error_field
    ):
        url, data = get_customer_test_data("create")

        for key, value in data_overrides.items():
            if value is None:
                data.pop(key, None)
            else:
                data[key] = value

        response = installer_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        if expected_error_field:
            assert expected_error_field in response.data


@pytest.mark.django_db
class TestRetrieveCustomer:
    """Test suite for customer retrieval endpoint."""

    def test_retrieve_customer_success(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        url, _ = get_customer_test_data("detail", customer_id=customer.id)

        response = installer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(customer.id)
        assert response.data["email"] == customer.email
        assert response.data["full_name"] == customer.full_name
        assert "full_address" in response.data

    def test_retrieve_customer_unauthenticated(self, api_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        url, _ = get_customer_test_data("detail", customer_id=customer.id)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_nonexistent_customer(self, installer_client):
        url, _ = get_customer_test_data("detail", customer_id=uuid.uuid4())
        response = installer_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateCustomer:
    """Test suite for customer update endpoint."""

    def test_update_customer_success(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        url = reverse("customers:customer-update", kwargs={"id": customer.id})
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": customer.email,
            "phone_number": "+9876543210",
            "address_line1": "456 Oak Ave",
            "city": "Munich",
            "state": "Bavaria",
            "postal_code": "80331",
            "country": "DE",
        }

        response = installer_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Jane"
        assert response.data["last_name"] == "Smith"
        assert response.data["phone_number"] == "+9876543210"
        customer.refresh_from_db()
        assert customer.first_name == "Jane"

    def test_update_customer_partial(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        url = reverse("customers:customer-update", kwargs={"id": customer.id})
        original_email = customer.email
        data = {"first_name": "UpdatedName"}

        response = installer_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "UpdatedName"
        assert response.data["email"] == original_email
        customer.refresh_from_db()
        assert customer.first_name == "UpdatedName"
        assert customer.email == original_email

    def test_update_customer_unauthenticated(self, api_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        url = reverse("customers:customer-update", kwargs={"id": customer.id})
        data = {"first_name": "Jane"}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_nonexistent_customer(self, installer_client):
        import uuid

        url = reverse("customers:customer-update", kwargs={"id": uuid.uuid4()})
        data = {"first_name": "Jane"}

        response = installer_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_customer_duplicate_email(self, installer_client, installer_user):
        customer1 = CustomerFactory(created_by=installer_user)
        CustomerFactory(email="existing@example.com", created_by=installer_user)
        url = reverse("customers:customer-update", kwargs={"id": customer1.id})
        data = {"email": "existing@example.com"}

        response = installer_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data


@pytest.mark.django_db
class TestDeleteCustomer:
    """Test suite for customer delete endpoint."""

    def test_delete_customer_success(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        customer_id = customer.id
        url = reverse("customers:customer-delete", kwargs={"id": customer_id})

        response = installer_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Customer.objects.filter(id=customer_id).exists()

    def test_delete_customer_unauthenticated(self, api_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        url = reverse("customers:customer-delete", kwargs={"id": customer.id})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Customer.objects.filter(id=customer.id).exists()

    def test_delete_nonexistent_customer(self, installer_client):
        url = reverse("customers:customer-delete", kwargs={"id": uuid.uuid4()})

        response = installer_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestListCustomer:
    """Test suite for customer list endpoint."""

    def test_list_customers_success(self, installer_client, installer_user):
        CustomerFactory.create_batch(3, created_by=installer_user)
        url, _ = get_customer_test_data("list")

        response = installer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 3

    def test_list_customers_unauthenticated(self, api_client):
        url, _ = get_customer_test_data("list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_customers_empty(self, installer_client):
        url, _ = get_customer_test_data("list")
        response = installer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert len(response.data["results"]) == 0


@pytest.mark.django_db
class TestCustomerModel:
    """Test suite for Customer model methods and properties."""

    def test_customer_full_name(self, installer_user):
        customer = CustomerFactory(
            first_name="John", last_name="Doe", created_by=installer_user
        )

        assert customer.full_name == "John Doe"

    def test_customer_full_address(self, installer_user):
        customer = CustomerFactory(
            address_line1="123 Main St",
            address_line2="Apt 4B",
            city="San Francisco",
            state="CA",
            postal_code="94102",
            country="US",
            created_by=installer_user,
        )

        assert "123 Main St" in customer.full_address
        assert "San Francisco" in customer.full_address
        assert "CA" in customer.full_address

    def test_customer_string_representation(self, installer_user):
        customer = CustomerFactory(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            created_by=installer_user,
        )

        assert str(customer) == "John Doe (john@example.com)"
