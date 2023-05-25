from django.urls import path
from . import views

app_name = 'markets'

urlpatterns = [
    path(("testing/"), views.MarketCreateView.as_view(), name="testing"), 
]