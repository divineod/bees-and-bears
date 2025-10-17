from django.contrib import admin

from .models import LoanOffer


@admin.register(LoanOffer)
class LoanOfferAdmin(admin.ModelAdmin):
    """Admin interface for LoanOffer model."""

    list_display = (
        "id",
        "customer",
        "loan_amount",
        "interest_rate",
        "loan_term",
        "monthly_payment",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "created_at", "interest_rate")
    search_fields = (
        "customer__first_name",
        "customer__last_name",
        "customer__email",
    )
    readonly_fields = ("monthly_payment", "created_at", "updated_at", "created_by")
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Customer",
            {
                "fields": ("customer",),
            },
        ),
        (
            "Loan Details",
            {
                "fields": ("loan_amount", "interest_rate", "loan_term"),
            },
        ),
        (
            "Calculated Payment",
            {
                "fields": ("monthly_payment",),
            },
        ),
        (
            "Status",
            {
                "fields": ("status",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
            },
        ),
    )
