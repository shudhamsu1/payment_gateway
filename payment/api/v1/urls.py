from django.urls import path

from payment.api.v1.viewsets import AddCash, BankDetailViewSet #HomePageView
from . import viewsets


urlpatterns = [
    path('add-cash/', AddCash.as_view(), name='add_cash'),
    path('add-bank/', BankDetailViewSet.as_view(), name='add_cash'),
    # path('', viewsets.HomePageView.as_view(),name='home'),
]
