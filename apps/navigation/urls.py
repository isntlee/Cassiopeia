from django.urls import path
from . import views

app_name = 'navigation'

urlpatterns = [
    path("", views.WaypointListView.as_view(), name="waypoint_list"), 
    path("create/", views.WaypointCreateView.as_view(), name="waypoint_create")
]