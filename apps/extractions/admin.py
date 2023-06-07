from django.contrib import admin
from .models import Extraction

class ExtractionAdmin(admin.ModelAdmin):
    list_display = ['extraction_name', 'extracted', 'units' , 'created_at']

admin.site.register(Extraction, ExtractionAdmin)