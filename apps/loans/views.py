from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.authentication.permissions import IsInstaller, IsInstallerOrOwner

from .models import LoanOffer
from .serializers import (
    LoanOfferCreateSerializer,
    LoanOfferListSerializer,
    LoanOfferSerializer,
)


@extend_schema_view(
    post=extend_schema(
        summary="Create a new loan offer",
        description="Create a loan offer with automatic monthly payment calculation",
        tags=["Loan Offers"],
        request=LoanOfferCreateSerializer,
        responses={201: LoanOfferSerializer},
    )
)
class LoanOfferCreateView(generics.CreateAPIView):
    queryset = LoanOffer.objects.all()
    serializer_class = LoanOfferCreateSerializer
    permission_classes = [IsInstaller]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LoanOfferCreateSerializer
        return LoanOfferSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve loan offer details",
        description="Get detailed information about a "
        "specific loan offer including payment breakdown",
        tags=["Loan Offers"],
    )
)
class LoanOfferRetrieveView(generics.RetrieveAPIView):
    queryset = LoanOffer.objects.select_related("customer", "created_by").all()
    serializer_class = LoanOfferSerializer
    permission_classes = [IsInstallerOrOwner]
    lookup_field = "id"


@extend_schema_view(
    get=extend_schema(
        summary="List all loan offers",
        description="Get a paginated list of all loan offers",
        tags=["Loan Offers"],
    )
)
class LoanOfferListView(generics.ListAPIView):
    serializer_class = LoanOfferListSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["customer", "status"]
    search_fields = ["customer__first_name", "customer__last_name", "customer__email"]
    ordering_fields = ["created_at", "loan_amount", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_installer:
            return LoanOffer.objects.select_related("customer", "created_by").all()
        else:
            if hasattr(user, "customer_profile") and user.customer_profile:
                return LoanOffer.objects.filter(
                    customer=user.customer_profile
                ).select_related("customer", "created_by")
            return LoanOffer.objects.none()


@extend_schema_view(
    put=extend_schema(
        summary="Update loan offer",
        description="Update loan offer information",
        tags=["Loan Offers"],
        request=LoanOfferCreateSerializer,
        responses={200: LoanOfferSerializer},
    ),
    patch=extend_schema(
        summary="Partially update loan offer",
        description="Partially update loan offer information",
        tags=["Loan Offers"],
        request=LoanOfferCreateSerializer,
        responses={200: LoanOfferSerializer},
    ),
)
class LoanOfferUpdateView(generics.UpdateAPIView):
    queryset = LoanOffer.objects.all()
    serializer_class = LoanOfferCreateSerializer
    permission_classes = [IsInstaller]
    lookup_field = "id"


@extend_schema_view(
    delete=extend_schema(
        summary="Delete loan offer",
        description="Delete a loan offer record",
        tags=["Loan Offers"],
    )
)
class LoanOfferDeleteView(generics.DestroyAPIView):
    queryset = LoanOffer.objects.all()
    permission_classes = [IsInstaller]
    lookup_field = "id"
