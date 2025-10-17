from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsSuperuserOrInstaller
from .serializers import (
    CustomerRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    InstallerCreateSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


@extend_schema_view(
    post=extend_schema(
        summary="Register a new customer user",
        description="Create a new customer user account",
        tags=["Authentication"],
    )
)
class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "message": "User registered successfully",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        summary="[DEV ONLY] Register customer account with full profile",
        description="Create customer account with user profile "
        "and address. DISABLED IN PRODUCTION (DEBUG=False).",
        tags=["Authentication"],
    )
)
class RegisterCustomerView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerRegistrationSerializer

    def post(self, request):
        if not settings.DEBUG:
            return Response(
                {
                    "detail": "Customer self-registration is disabled in production. "
                    "Please contact an installer to create your account."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            user = result["user"]
            customer = result["customer"]

            return Response(
                {
                    "user": {
                        "id": str(user.id),
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    },
                    "customer": {
                        "id": str(customer.id),
                        "full_name": customer.full_name,
                        "email": customer.email,
                        "city": customer.city,
                        "state": customer.state,
                    },
                    "message": "Customer account created successfully. "
                    "You can now login with your email and password.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        summary="Create a new installer user",
        description="Create a new installer user account. "
        "Only accessible by superusers and existing installers.",
        tags=["Customers"],
    )
)
class CreateInstallerView(APIView):
    permission_classes = [IsSuperuserOrInstaller]
    serializer_class = InstallerCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "message": "Installer created successfully",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        summary="Get current user profile",
        description="Retrieve the authenticated user's profile information",
        tags=["Authentication"],
    )
)
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema_view(
    put=extend_schema(
        summary="Update current user profile",
        description="Update the authenticated user's profile information",
        tags=["Authentication"],
    ),
    patch=extend_schema(
        summary="Partially update current user profile",
        description="Partially update the authenticated user's profile information",
        tags=["Authentication"],
    ),
)
class CurrentUserUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema_view(
    post=extend_schema(
        summary="Login to get JWT tokens",
        description="Authenticate and receive access and refresh tokens",
        tags=["Authentication"],
    )
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
