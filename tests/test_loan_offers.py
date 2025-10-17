import uuid
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from apps.loans.models import LoanOffer
from tests.factories import CustomerFactory, LoanOfferFactory


@pytest.mark.django_db
class TestCreateLoanOffer:
    """Test suite for loan offer creation endpoint."""

    def test_create_loan_offer_success(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        url = reverse("loans:loanoffer-create")
        data = {
            "customer": customer.id,
            "loan_amount": "10000.00",
            "interest_rate": "5.00",
            "loan_term": 60,
        }

        response = installer_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert LoanOffer.objects.filter(customer=customer).exists()
        
        loan_offer = LoanOffer.objects.get(customer=customer)
        assert loan_offer.monthly_payment > 0
        assert loan_offer.created_by == installer_user

    def test_create_loan_offer_unauthenticated(self, api_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        url = reverse("loans:loanoffer-create")
        data = {
            "customer": customer.id,
            "loan_amount": "10000.00",
            "interest_rate": "5.00",
            "loan_term": 60,
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "loan_amount,interest_rate,loan_term,expected_error_field",
        [
            ("-1000.00", "5.00", 60, "loan_amount"),
            ("2000000.00", "5.00", 60, "loan_amount"),
            ("10000.00", "-5.00", 60, "interest_rate"),
            ("10000.00", "5.00", 0, "loan_term"),
        ],
        ids=[
            "negative_loan_amount",
            "excessive_loan_amount",
            "negative_interest_rate",
            "zero_loan_term",
        ],
    )
    def test_create_loan_offer_validation_errors(
        self,
        installer_client,
        installer_user,
        loan_amount,
        interest_rate,
        loan_term,
        expected_error_field,
    ):
        customer = CustomerFactory(created_by=installer_user)
        url = reverse("loans:loanoffer-create")
        data = {
            "customer": customer.id,
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "loan_term": loan_term,
        }

        response = installer_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert expected_error_field in response.data

    def test_create_loan_offer_zero_interest(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        url = reverse("loans:loanoffer-create")
        data = {
            "customer": customer.id,
            "loan_amount": "12000.00",
            "interest_rate": "0.00",
            "loan_term": 12,
        }

        response = installer_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        loan_offer = LoanOffer.objects.get(customer=customer)
        expected_payment = Decimal("12000.00") / 12
        assert loan_offer.monthly_payment == expected_payment.quantize(Decimal("0.01"))


@pytest.mark.django_db
class TestRetrieveLoanOffer:
    """Test suite for loan offer retrieval endpoint."""

    def test_retrieve_loan_offer_success(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(customer=customer, created_by=installer_user)
        url = reverse("loans:loanoffer-detail", kwargs={"id": loan_offer.id})

        response = installer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(loan_offer.id)
        assert Decimal(response.data["loan_amount"]) == loan_offer.loan_amount
        assert "monthly_payment" in response.data
        assert "total_payment" in response.data
        assert "total_interest" in response.data
        assert "customer_details" in response.data

    def test_retrieve_loan_offer_unauthenticated(self, api_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(customer=customer, created_by=installer_user)
        url = reverse("loans:loanoffer-detail", kwargs={"id": loan_offer.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_nonexistent_loan_offer(self, installer_client):
        url = reverse("loans:loanoffer-detail", kwargs={"id": uuid.uuid4()})
        response = installer_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateLoanOffer:
    """Test suite for loan offer update endpoint."""

    def test_update_loan_offer_success(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(customer=customer, created_by=installer_user)
        url = reverse("loans:loanoffer-update", kwargs={"id": loan_offer.id})
        data = {
            "customer": customer.id,
            "loan_amount": "15000.00",
            "interest_rate": "6.50",
            "loan_term": 48,
        }

        response = installer_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data["loan_amount"]) == Decimal("15000.00")
        assert Decimal(response.data["interest_rate"]) == Decimal("6.50")
        assert response.data["loan_term"] == 48
        loan_offer.refresh_from_db()
        assert loan_offer.loan_amount == Decimal("15000.00")

    def test_update_loan_offer_partial(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(
            customer=customer,
            loan_amount=Decimal("10000.00"),
            created_by=installer_user,
        )
        url = reverse("loans:loanoffer-update", kwargs={"id": loan_offer.id})
        original_amount = loan_offer.loan_amount
        data = {"interest_rate": "7.00"}

        response = installer_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data["interest_rate"]) == Decimal("7.00")
        assert Decimal(response.data["loan_amount"]) == original_amount
        loan_offer.refresh_from_db()
        assert loan_offer.interest_rate == Decimal("7.00")
        assert loan_offer.loan_amount == original_amount

    def test_update_loan_offer_unauthenticated(self, api_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(customer=customer, created_by=installer_user)
        url = reverse("loans:loanoffer-update", kwargs={"id": loan_offer.id})
        data = {"interest_rate": "7.00"}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_nonexistent_loan_offer(self, installer_client):
        url = reverse("loans:loanoffer-update", kwargs={"id": uuid.uuid4()})
        data = {"interest_rate": "7.00"}

        response = installer_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_loan_offer_validation_errors(
        self, installer_client, installer_user
    ):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(customer=customer, created_by=installer_user)
        url = reverse("loans:loanoffer-update", kwargs={"id": loan_offer.id})
        data = {"loan_amount": "-5000.00"}

        response = installer_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "loan_amount" in response.data


@pytest.mark.django_db
class TestDeleteLoanOffer:
    """Test suite for loan offer delete endpoint."""

    def test_delete_loan_offer_success(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(customer=customer, created_by=installer_user)
        loan_offer_id = loan_offer.id
        url = reverse("loans:loanoffer-delete", kwargs={"id": loan_offer_id})

        response = installer_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not LoanOffer.objects.filter(id=loan_offer_id).exists()

    def test_delete_loan_offer_unauthenticated(self, api_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(customer=customer, created_by=installer_user)
        url = reverse("loans:loanoffer-delete", kwargs={"id": loan_offer.id})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert LoanOffer.objects.filter(id=loan_offer.id).exists()

    def test_delete_nonexistent_loan_offer(self, installer_client):
        url = reverse("loans:loanoffer-delete", kwargs={"id": uuid.uuid4()})
        response = installer_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestListLoanOffers:
    """Test suite for loan offer list endpoint."""

    def test_list_loan_offers_success(self, installer_client, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        LoanOfferFactory.create_batch(3, customer=customer, created_by=installer_user)
        url = reverse("loans:loanoffer-list")

        response = installer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 3

    def test_list_loan_offers_unauthenticated(self, api_client):
        url = reverse("loans:loanoffer-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_loan_offers_empty(self, installer_client):
        url = reverse("loans:loanoffer-list")
        response = installer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0


@pytest.mark.django_db
class TestLoanCalculations:
    """Test suite for loan payment calculations."""

    @pytest.mark.parametrize(
        "loan_amount,interest_rate,loan_term,expected_min,expected_max",
        [
            (
                Decimal("10000.00"),
                Decimal("5.00"),
                60,
                Decimal("188.00"),
                Decimal("189.00"),
            ),
            (
                Decimal("12000.00"),
                Decimal("0.00"),
                12,
                Decimal("1000.00"),
                Decimal("1000.00"),
            ),
            (
                Decimal("10000.00"),
                Decimal("15.00"),
                36,
                Decimal("346.00"),
                Decimal("348.00"),
            ),
            (
                Decimal("5000.00"),
                Decimal("10.00"),
                12,
                Decimal("439.00"),
                Decimal("441.00"),
            ),
        ],
        ids=["standard", "zero_interest", "high_interest_rate", "short_term_loan"],
    )
    def test_monthly_payment_calculation(
        self,
        installer_user,
        loan_amount,
        interest_rate,
        loan_term,
        expected_min,
        expected_max,
    ):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(
            customer=customer,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            loan_term=loan_term,
            created_by=installer_user,
        )

        assert loan_offer.monthly_payment >= expected_min
        assert loan_offer.monthly_payment <= expected_max

    def test_total_payment_calculation(self, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(
            customer=customer,
            loan_amount=Decimal("10000.00"),
            interest_rate=Decimal("5.00"),
            loan_term=60,
            created_by=installer_user,
        )

        total_payment = loan_offer.total_payment
        assert total_payment > loan_offer.loan_amount
        assert total_payment == loan_offer.monthly_payment * loan_offer.loan_term

    def test_total_interest_calculation(self, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(
            customer=customer,
            loan_amount=Decimal("10000.00"),
            interest_rate=Decimal("5.00"),
            loan_term=60,
            created_by=installer_user,
        )

        total_interest = loan_offer.total_interest
        assert total_interest > 0
        assert total_interest == loan_offer.total_payment - loan_offer.loan_amount


@pytest.mark.django_db
class TestLoanOfferModel:
    """Test suite for LoanOffer model methods and properties."""

    def test_loan_offer_string_representation(self, installer_user):
        customer = CustomerFactory(
            first_name="John", last_name="Doe", created_by=installer_user
        )
        loan_offer = LoanOfferFactory(
            customer=customer,
            loan_amount=Decimal("10000.00"),
            created_by=installer_user,
        )

        assert "John Doe" in str(loan_offer)
        assert "$10000" in str(loan_offer)

    def test_loan_offer_status_default(self, installer_user):
        customer = CustomerFactory(created_by=installer_user)
        loan_offer = LoanOfferFactory(customer=customer, created_by=installer_user)

        assert loan_offer.status == "PENDING"
