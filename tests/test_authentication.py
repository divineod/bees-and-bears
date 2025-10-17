import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from tests.factories import UserFactory

User = get_user_model()


def get_auth_test_data(endpoint, **kwargs):
    """
    Helper function to get URL and data for authentication endpoints.

    Args:
        endpoint: The endpoint name ('register', 'login', 'token_refresh')
        **kwargs: Override default values for any field

    Returns:
        tuple: (url, data) for the test
    """
    urls = {
        "register": reverse("authentication:register"),
        "login": reverse("authentication:login"),
        "token_refresh": reverse("authentication:token_refresh"),
    }

    default_data = {
        "register": {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        },
        "login": {
            "username": "testuser",
            "password": "testpass123",
        },
        "token_refresh": {
            "refresh": "",
        },
    }

    url = urls.get(endpoint)
    data = {**default_data.get(endpoint, {}), **kwargs}

    return url, data


@pytest.mark.django_db
class TestUserRegistration:
    """Test suite for user registration endpoint."""

    def test_register_user_success(self, api_client):
        url, data = get_auth_test_data("register")

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["username"] == "newuser"
        assert response.data["email"] == "newuser@example.com"
        assert "password" not in response.data
        assert User.objects.filter(username="newuser").exists()

    def test_register_user_password_mismatch(self, api_client):
        url, data = get_auth_test_data("register", password_confirm="DifferentPass123!")

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data
        assert not User.objects.filter(username="newuser").exists()

    def test_register_user_duplicate_email(self, api_client):
        UserFactory(email="existing@example.com")
        url, data = get_auth_test_data("register", email="existing@example.com")

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_user_missing_fields(self, api_client):
        url, _ = get_auth_test_data("register")
        data = {"username": "newuser"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data or "password" in response.data


@pytest.mark.django_db
class TestUserLogin:
    """Test suite for user login endpoint."""

    def test_login_success(self, api_client, user):
        url, data = get_auth_test_data("login")

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["username"] == "testuser"
        assert response.data["user"]["email"] == "testuser@example.com"

    def test_login_invalid_credentials(self, api_client, user):
        url, data = get_auth_test_data("login", password="wrongpassword")

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        url, data = get_auth_test_data(
            "login", username="nonexistent", password="somepassword"
        )

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "username,password",
        [
            ("testuser", None),
            (None, "testpass123"),
            (None, None),
        ],
        ids=["missing_password", "missing_username", "missing_both"],
    )
    def test_login_missing_fields(self, api_client, username, password):
        url, _ = get_auth_test_data("login")
        data = {}
        if username is not None:
            data["username"] = username
        if password is not None:
            data["password"] = password

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTokenRefresh:
    """Test suite for token refresh endpoint."""

    def test_refresh_token_success(self, api_client, user):
        login_url, login_data = get_auth_test_data("login")
        login_response = api_client.post(login_url, login_data, format="json")
        refresh_token = login_response.data["refresh"]

        refresh_url, refresh_data = get_auth_test_data(
            "token_refresh", refresh=refresh_token
        )
        response = api_client.post(refresh_url, refresh_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_refresh_token_invalid(self, api_client):
        url, data = get_auth_test_data("token_refresh", refresh="invalid_token")

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
