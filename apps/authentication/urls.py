from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CreateInstallerView,
    CurrentUserUpdateView,
    CurrentUserView,
    CustomTokenObtainPairView,
    RegisterCustomerView,
    RegisterView,
)

app_name = "authentication"

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path(
        "register-customer",
        RegisterCustomerView.as_view(),
        name="register_customer",
    ),
    path("installers/create", CreateInstallerView.as_view(), name="create_installer"),
    path("login", CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("me", CurrentUserView.as_view(), name="current_user"),
    path("me/update", CurrentUserUpdateView.as_view(), name="current_user_update"),
]
