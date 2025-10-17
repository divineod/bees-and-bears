from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.authentication.permissions import IsInstaller, IsInstallerOrOwner

from .models import Customer
from .serializers import CustomerListSerializer, CustomerSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Create a new customer",
        description="Create a new customer record for loan applications",
        tags=["Customers"],
    )
)
class CustomerCreateView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsInstaller]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve customer details",
        description="Get detailed information about a specific customer",
        tags=["Customers"],
    )
)
class CustomerRetrieveView(generics.RetrieveAPIView):
    queryset = Customer.objects.select_related("created_by").all()
    serializer_class = CustomerSerializer
    permission_classes = [IsInstallerOrOwner]
    lookup_field = "id"


@extend_schema_view(
    get=extend_schema(
        summary="List all customers",
        description="Get a paginated list of all customers",
        tags=["Customers"],
    )
)
class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerListSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["email", "city", "state"]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["created_at", "last_name", "first_name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_installer:
            return Customer.objects.select_related("created_by").all()
        else:
            if hasattr(user, "customer_profile") and user.customer_profile:
                return Customer.objects.filter(id=user.customer_profile.id)
            return Customer.objects.none()


@extend_schema_view(
    put=extend_schema(
        summary="Update customer",
        description="Update customer information",
        tags=["Customers"],
    ),
    patch=extend_schema(
        summary="Partially update customer",
        description="Partially update customer information",
        tags=["Customers"],
    ),
)
class CustomerUpdateView(generics.UpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsInstaller]
    lookup_field = "id"


@extend_schema_view(
    delete=extend_schema(
        summary="Delete customer",
        description="Delete a customer record",
        tags=["Customers"],
    )
)
class CustomerDeleteView(generics.DestroyAPIView):
    queryset = Customer.objects.all()
    permission_classes = [IsInstaller]
    lookup_field = "id"
