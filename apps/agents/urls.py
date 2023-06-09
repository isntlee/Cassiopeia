from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    path(("testing/"), views.AgentCreateView.as_view(), name="testing"), 
]