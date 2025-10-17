from django.urls import path

from .views import (
    CustomerCreateView,
    CustomerDeleteView,
    CustomerListView,
    CustomerRetrieveView,
    CustomerUpdateView,
)

app_name = "customers"

urlpatterns = [
    path("", CustomerCreateView.as_view(), name="customer-create"),
    path("list", CustomerListView.as_view(), name="customer-list"),
    path("<uuid:id>", CustomerRetrieveView.as_view(), name="customer-detail"),
    path("<uuid:id>/update", CustomerUpdateView.as_view(), name="customer-update"),
    path("<uuid:id>/delete", CustomerDeleteView.as_view(), name="customer-delete"),
]
