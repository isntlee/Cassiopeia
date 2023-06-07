from django.urls import path
from . import views

app_name = 'navigation'

urlpatterns = [
    path(("testing/"), views.WaypointCreateView.as_view(), name="testing"), 
]