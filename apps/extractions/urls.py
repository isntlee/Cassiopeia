from django.urls import path
from . import views

app_name = 'extractions'

urlpatterns = [
    path(("testing/"), views.ExtractionCreateView.as_view(), name="testing"), 
]