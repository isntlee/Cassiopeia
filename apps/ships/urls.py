from django.urls import path
from . import views

app_name = 'ships'

urlpatterns = [
    path("", views.ShipListView.as_view(), name="ship_list"), 
    path(("create/"), views.create_ship_or_cargo, name='create_ship_or_cargo'), 
]
