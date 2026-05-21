from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'due_date')
    list_filter = ('status',)
    search_fields = ('name',)
