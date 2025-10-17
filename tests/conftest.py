"""
Pytest configuration and fixtures for the test suite.
"""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories import (
    CustomerFactory,
    CustomerUserFactory,
    InstallerUserFactory,
    LoanOfferFactory,
    UserFactory,
)


@pytest.fixture
def api_client():
    """
    Create an Unauthenticated API client for testing.
    """
    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory(
        username="testuser",
        email="testuser@example.com",
    )


@pytest.fixture
def installer_user(db):
    return InstallerUserFactory(
        username="installer",
        email="installer@example.com",
    )


@pytest.fixture
def customer_user(db):
    return CustomerUserFactory(
        username="customer",
        email="customer@example.com",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Fixture to provide an authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def installer_client(api_client, installer_user):
    """Fixture to provide an authenticated API client with installer permissions."""
    refresh = RefreshToken.for_user(installer_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def customer_client(api_client, customer_user):
    """Fixture to provide an authenticated API client with customer permissions."""
    refresh = RefreshToken.for_user(customer_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def another_user(db):
    """Fixture to create another test user."""
    return UserFactory(
        username="anotheruser",
        email="anotheruser@example.com",
    )


@pytest.fixture
def customer(db, installer_user):
    """Fixture to create a customer linked to installer_user."""
    return CustomerFactory(created_by=installer_user)


@pytest.fixture
def customer_with_profile(db, installer_user, customer_user):
    """Fixture to create a customer linked to both installer and customer user."""
    return CustomerFactory(created_by=installer_user, user=customer_user)


@pytest.fixture
def loan_offer(db, customer, installer_user):
    """Fixture to create a loan offer."""
    return LoanOfferFactory(customer=customer, created_by=installer_user)
