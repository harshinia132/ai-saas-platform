from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg
from tasks.models import Task
from users.models import User
from ai_service import AIService

@staff_member_required
def ai_dashboard(request):
    ai_service = AIService()
    
    # Get statistics
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='completed').count()
    pending_tasks = total_tasks - completed_tasks
    
    # Get AI productivity insight
    insight = ai_service.get_productivity_insight(completed_tasks, pending_tasks)
    
    # Get high priority tasks
    high_priority_tasks = Task.objects.filter(priority__in=['high', 'urgent'])[:5]
    
    context = {
        'insight': insight,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        'high_priority_tasks': high_priority_tasks,
    }
    
    return render(request, 'ai_dashboard.html', context)
