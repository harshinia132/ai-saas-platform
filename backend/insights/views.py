from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tasks.models import Task
from projects.models import Project

try:
    from ai_service import AIService
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

@login_required
def ai_dashboard(request):
    user = request.user
    
    # Different data based on role
    if user.role in ['manager', 'org_admin', 'super_admin'] or user.is_superuser:
        # Managers see all data
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status='completed').count()
        total_projects = Project.objects.count()
        high_priority_tasks = Task.objects.filter(priority__in=['high', 'urgent'])[:5]
        is_manager = True
    else:
        # Employees only see their own data
        total_tasks = Task.objects.filter(assignee=user).count()
        completed_tasks = Task.objects.filter(assignee=user, status='completed').count()
        total_projects = Project.objects.filter(team_members=user).count()
        high_priority_tasks = Task.objects.filter(assignee=user, priority__in=['high', 'urgent'])[:5]
        is_manager = False
    
    pending_tasks = total_tasks - completed_tasks
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get AI productivity insight
    insight = "Stay focused and prioritize your most important tasks first!"
    if AI_AVAILABLE:
        try:
            ai_service = AIService()
            if ai_service.is_available:
                insight = ai_service.get_productivity_insight(completed_tasks, pending_tasks)
        except:
            pass
    
    context = {
        'insight': insight,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': completion_rate,
        'high_priority_tasks': high_priority_tasks,
        'total_projects': total_projects,
        'ai_available': AI_AVAILABLE,
        'is_manager': is_manager,
        'user_role': user.role,
    }
    
    return render(request, 'insights/ai_dashboard.html', context)
