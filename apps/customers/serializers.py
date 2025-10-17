from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Customer

User = get_user_model()


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model with comprehensive validation."""

    full_name = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Customer
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "full_address",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")

        queryset = Customer.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "A customer with this email already exists."
            )

        return value.lower()

    def validate_phone_number(self, value):
        if value:
            cleaned = (
                value.replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
            )
            if not cleaned.replace("+", "").isdigit():
                raise serializers.ValidationError(
                    "Phone number must contain only digits and separators."
                )
        return value

    def validate_postal_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Postal code is required.")
        return value.strip()

    def create(self, validated_data):
        email = validated_data.get("email")

        user = User.objects.create_user(
            username=email,
            email=email,
            role=User.Role.CUSTOMER,
        )
        user.set_unusable_password()
        user.save()

        validated_data["user"] = user

        return super().create(validated_data)


class CustomerListSerializer(serializers.ModelSerializer):
    """Serializer for customer list view."""

    full_name = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Customer
        fields = (
            "id",
            "full_name",
            "email",
            "phone_number",
            "city",
            "state",
            "created_by_username",
            "created_at",
        )
