from django.urls import path
from . import views

app_name = 'navigation'

urlpatterns = [
    path(("testing/"), views.WaypointsCreateView.as_view(), name="testing"), 
]