from django.contrib import admin
from .models import Task

# Import AI service
from ai_service import AIService

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assignee', 'due_date', 'ai_priority_score')
    list_filter = ('status', 'priority')
    search_fields = ('title',)
    readonly_fields = ('ai_priority_score',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'project', 'assignee')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'due_date')
        }),
        ('AI Insights', {
            'fields': ('ai_priority_score',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Initialize AI service
        ai_service = AIService()
        
        # Call AI before saving (for new tasks)
        if not change:
            try:
                # Get AI priority suggestion
                suggested_priority = ai_service.get_task_priority_suggestion(
                    obj.title, 
                    obj.description or ""
                )
                
                # Map AI suggestion to priority score
                priority_map = {'Low': 25, 'Medium': 50, 'High': 75, 'Urgent': 100}
                obj.ai_priority_score = priority_map.get(suggested_priority, 50)
                
                # If AI suggests a priority, update the task priority
                if suggested_priority in ['Low', 'Medium', 'High', 'Urgent']:
                    obj.priority = suggested_priority.lower()
                
                # Get AI breakdown
                breakdown = ai_service.get_task_breakdown(obj.title)
                
                # Get AI duration estimate
                estimated_hours = ai_service.estimate_task_duration(obj.title, 5)
                
                # Store AI recommendations
                obj.ai_recommendations = {
                    'suggested_priority': suggested_priority,
                    'breakdown': breakdown,
                    'estimated_hours': estimated_hours,
                    'ai_analyzed': True
                }
                
                print(f"AI Analysis complete for task: {obj.title}")
                print(f"  Suggested Priority: {suggested_priority}")
                print(f"  Estimated Hours: {estimated_hours}")
                
            except Exception as e:
                print(f"AI Error: {e}")
                obj.ai_priority_score = 50
                obj.ai_recommendations = {'error': str(e), 'ai_analyzed': False}
        else:
            if not obj.ai_recommendations:
                obj.ai_recommendations = {}
        
        super().save_model(request, obj, form, change)
