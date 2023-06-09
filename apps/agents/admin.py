from django.contrib import admin
from .models import Agent

class AgentAdmin(admin.ModelAdmin):
    list_display = ['symbol']

admin.site.register(Agent, AgentAdmin)