from django.urls import path
from . import views

app_name = 'ships'

urlpatterns = [
    path(("testing/"), views.create_ship_or_cargo, name='create_ship_or_cargo'), 
]