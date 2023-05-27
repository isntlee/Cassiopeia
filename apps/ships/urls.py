from django.urls import path
from . import views

app_name = 'ships'

urlpatterns = [
    path(("testing/"), views.ShipCreateView.as_view(), name="testing"), 
]