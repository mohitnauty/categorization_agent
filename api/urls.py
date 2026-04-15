from django.urls import path
from .views import categorize_transaction

urlpatterns = [
    path('categorize/', categorize_transaction),
]