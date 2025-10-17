import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from apps.customers.models import Customer

User = get_user_model()


class LoanOffer(models.Model):
    """
    LoanOffer model representing loan applications for green technology financing.

    This model handles loan calculations using standard amortization formulas.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("DISBURSED", "Disbursed"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="loan_offers",
        db_index=True,
    )
    loan_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        blank=False,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Principal loan amount in EUR",
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=False,
        blank=False,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Annual percentage rate- APR",
    )
    loan_term = models.IntegerField(
        null=False,
        blank=False,
        validators=[MinValueValidator(1)],
        help_text="Loan term in months",
    )
    monthly_payment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text="Calculated monthly payment amount",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="loan_offers_created",
        help_text="The user (installer) who created this loan offer",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["created_by", "created_at"]),
        ]
        verbose_name = "Loan Offer"
        verbose_name_plural = "Loan Offers"

    def __str__(self):
        return f"Loan #{self.pk} - {self.customer.full_name} - ${self.loan_amount}"

    def calculate_monthly_payment(self):
        """
        Calculate monthly payment using the standard loan amortization formula.

        Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        Where:
            M = Monthly payment
            P = Principal (loan amount)
            r = Monthly interest rate (annual rate / 12 / 100)
            n = Number of payments (loan term in months)

        For zero interest rate loans, monthly payment = principal / term
        """
        principal = Decimal(str(self.loan_amount))
        annual_rate = Decimal(str(self.interest_rate))
        term_months = int(self.loan_term)

        if annual_rate == 0:
            return (principal / term_months).quantize(Decimal("0.01"))

        monthly_rate = annual_rate / Decimal("100") / Decimal("12")

        numerator = monthly_rate * pow(1 + monthly_rate, term_months)
        denominator = pow(1 + monthly_rate, term_months) - 1

        monthly_payment = principal * (numerator / denominator)

        return monthly_payment.quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        self.monthly_payment = self.calculate_monthly_payment()
        super().save(*args, **kwargs)

    @property
    def total_payment(self):
        return (self.monthly_payment * self.loan_term).quantize(Decimal("0.01"))

    @property
    def total_interest(self):
        return (self.total_payment - self.loan_amount).quantize(Decimal("0.01"))
