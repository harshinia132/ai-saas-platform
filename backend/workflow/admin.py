from django.contrib import admin
from .models import Workflow, WorkflowInstance

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('name', 'workflow_type', 'is_active', 'created_at')
    list_filter = ('workflow_type', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'task', 'status', 'current_step_id')
    list_filter = ('status',)
    search_fields = ('task__title',)
