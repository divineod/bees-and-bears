from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin interface for Customer model."""

    list_display = (
        "id",
        "full_name",
        "email",
        "city",
        "state",
        "created_by",
        "created_at",
    )
    list_filter = ("state", "country", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone_number")
    readonly_fields = ("created_at", "updated_at", "created_by")
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": ("first_name", "last_name", "email", "phone_number"),
            },
        ),
        (
            "Address",
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    "city",
                    "state",
                    "postal_code",
                    "country",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
            },
        ),
    )
