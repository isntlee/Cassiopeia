from django.urls import path
from . import views

app_name = 'markets'

urlpatterns = [
    path(("testing/create"), views.MarketCreateView.as_view(), name="market_create"), 
    path(("testing/list"), views.MarketListView.as_view(), name="market_list"), 
]