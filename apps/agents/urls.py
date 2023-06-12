from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    path(("root"), views.AgentCreateView.as_view(), name="root"), 
]