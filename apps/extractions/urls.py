from django.urls import path
from . import views

app_name = 'extractions'

urlpatterns = [
    path(("testing/"), views.ExtractionCreateView.as_view(), name="testing"), 
]

app_name = 'extractions'

urlpatterns = [
    path("", views.ExtractionListView.as_view(), name="extraction_list"), 
    path("create/", views.ExtractionCreateView.as_view(), name="extraction_create")
]
