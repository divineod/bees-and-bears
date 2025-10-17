from decimal import Decimal

from rest_framework import serializers

from apps.customers.serializers import CustomerSerializer

from .models import LoanOffer


class LoanOfferSerializer(serializers.ModelSerializer):
    """Serializer for LoanOffer model with validation and calculations."""

    customer_details = CustomerSerializer(source="customer", read_only=True)
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )
    total_payment = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    total_interest = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = LoanOffer
        fields = (
            "id",
            "customer",
            "customer_details",
            "loan_amount",
            "interest_rate",
            "loan_term",
            "monthly_payment",
            "total_payment",
            "total_interest",
            "status",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "monthly_payment",
            "created_by",
            "created_at",
            "updated_at",
        )

    def validate_loan_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be greater than zero.")

        if value > Decimal("1000000.00"):
            raise serializers.ValidationError(
                "Loan amount cannot exceed $1,000,000.00."
            )

        return value

    def validate_interest_rate(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Interest rate cannot be negative. Use 0 for interest-free loans."
            )

        if value > Decimal("50.00"):
            raise serializers.ValidationError("Interest rate cannot exceed 50%.")

        return value

    def validate_loan_term(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan term must be at least 1 month.")

        if value > 360:
            raise serializers.ValidationError(
                "Loan term cannot exceed 360 months (30 years)."
            )

        return value

    def validate_customer(self, value):
        if not value:
            raise serializers.ValidationError("Customer is required.")
        return value

    def validate(self, attrs):
        loan_amount = attrs.get("loan_amount")
        interest_rate = attrs.get("interest_rate")
        loan_term = attrs.get("loan_term")

        if not all([loan_amount, loan_term, interest_rate is not None]):
            raise serializers.ValidationError(
                "Loan amount, interest rate, and loan term are required."
            )

        return attrs

    def create(self, validated_data):
        return super().create(validated_data)


class LoanOfferListSerializer(serializers.ModelSerializer):
    """Serializer for loan offer list view."""

    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = LoanOffer
        fields = (
            "id",
            "customer",
            "customer_name",
            "customer_email",
            "loan_amount",
            "interest_rate",
            "loan_term",
            "monthly_payment",
            "status",
            "created_by_username",
            "created_at",
        )


class LoanOfferCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating loan offers with customer ID."""

    class Meta:
        model = LoanOffer
        fields = (
            "id",
            "customer",
            "loan_amount",
            "interest_rate",
            "loan_term",
        )

    def validate_loan_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be greater than zero.")

        if value > Decimal("1000000.00"):
            raise serializers.ValidationError(
                "Loan amount cannot exceed $1,000,000.00."
            )

        return value

    def validate_interest_rate(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Interest rate cannot be negative. Use 0 for interest-free loans."
            )

        if value > Decimal("50.00"):
            raise serializers.ValidationError("Interest rate cannot exceed 50%.")

        return value

    def validate_loan_term(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan term must be at least 1 month.")

        if value > 360:
            raise serializers.ValidationError(
                "Loan term cannot exceed 360 months (30 years)."
            )

        return value
