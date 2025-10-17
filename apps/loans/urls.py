from django.urls import path

from .views import (
    LoanOfferCreateView,
    LoanOfferDeleteView,
    LoanOfferListView,
    LoanOfferRetrieveView,
    LoanOfferUpdateView,
)

app_name = "loans"

urlpatterns = [
    path("", LoanOfferCreateView.as_view(), name="loanoffer-create"),
    path("list", LoanOfferListView.as_view(), name="loanoffer-list"),
    path("<uuid:id>", LoanOfferRetrieveView.as_view(), name="loanoffer-detail"),
    path("<uuid:id>/update", LoanOfferUpdateView.as_view(), name="loanoffer-update"),
    path("<uuid:id>/delete", LoanOfferDeleteView.as_view(), name="loanoffer-delete"),
]
