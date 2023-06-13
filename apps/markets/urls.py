from django.urls import path
from . import views

app_name = 'markets'

urlpatterns = [
    path("", views.MarketListView.as_view(), name="market_list"), 
    path("create/", views.MarketCreateView.as_view(), name="market_create")
]
