import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """
    Custom User model with role-based access control.

    Roles:
    - INSTALLER: Can create customers and loan offers, view all data
    - CUSTOMER: Can only view their own customer record and loan offers
    """

    class Role(models.TextChoices):
        INSTALLER = "INSTALLER", "Installer"
        CUSTOMER = "CUSTOMER", "Customer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text="User role determining access permissions",
    )

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_installer(self):
        return self.role == self.Role.INSTALLER

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER
