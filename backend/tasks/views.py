from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Task
from projects.models import Project
from users.models import User

def is_manager(user):
    return user.role in ['manager', 'org_admin', 'super_admin'] or user.is_superuser

# Task List (RBAC: Managers see all, Employees see only assigned)
@login_required
def task_list(request):
    if is_manager(request.user):
        tasks = Task.objects.all()
        can_edit = True
    else:
        tasks = Task.objects.filter(assignee=request.user)
        can_edit = False
    
    # Get AI insight for tasks
    from ai_service import AIService
    ai = AIService()
    if tasks.count() > 0:
        insight = ai.get_productivity_insight(
            tasks.filter(status='completed').count(),
            tasks.exclude(status='completed').count()
        )
    else:
        insight = "Create your first task to get AI insights!"
    
    context = {
        'tasks': tasks,
        'can_edit': can_edit,
        'is_manager': is_manager(request.user),
        'insight': insight,
    }
    return render(request, 'tasks/list.html', context)

# Create Task (Only Managers)
@login_required
@user_passes_test(is_manager)
def task_create(request):
    projects = Project.objects.all()
    users = User.objects.filter(is_active=True)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        project_id = request.POST.get('project')
        assignee_id = request.POST.get('assignee')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date') or None
        
        # Get AI priority suggestion
        from ai_service import AIService
        ai = AIService()
        ai_priority = ai.get_task_priority_suggestion(title, description)
        
        task = Task.objects.create(
            title=title,
            description=description,
            project_id=project_id,
            assignee_id=assignee_id,
            created_by=request.user,
            priority=priority,
            due_date=due_date if due_date else None,
            ai_priority_score={'Low': 25, 'Medium': 50, 'High': 75, 'Urgent': 100}.get(ai_priority, 50)
        )
        messages.success(request, f'Task "{title}" created with AI priority: {ai_priority}!')
        return redirect('task_list')
    
    context = {
        'projects': projects,
        'users': users,
    }
    return render(request, 'tasks/create.html', context)

# Task Detail
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Check access
    if not is_manager(request.user) and task.assignee != request.user:
        messages.error(request, 'You do not have access to this task.')
        return redirect('task_list')
    
    context = {
        'task': task,
        'is_manager': is_manager(request.user),
    }
    return render(request, 'tasks/detail.html', context)

# Edit Task (Only Managers)
@login_required
@user_passes_test(is_manager)
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    projects = Project.objects.all()
    users = User.objects.filter(is_active=True)
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.project_id = request.POST.get('project')
        task.assignee_id = request.POST.get('assignee')
        task.priority = request.POST.get('priority')
        task.status = request.POST.get('status')
        
        due_date = request.POST.get('due_date')
        if due_date and due_date.strip():
            task.due_date = due_date
        else:
            task.due_date = None
        
        task.save()
        messages.success(request, f'Task "{task.title}" updated successfully!')
        return redirect('task_list')
    
    context = {
        'task': task,
        'projects': projects,
        'users': users,
        'is_manager': is_manager(request.user),
    }
    return render(request, 'tasks/edit.html', context)

# Delete Task (Only Managers)
@login_required
@user_passes_test(is_manager)
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted!')
        return redirect('task_list')
    
    return render(request, 'tasks/delete.html', {'task': task})

# Complete Task (Both roles can complete their own tasks)
@login_required
def task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user can complete this task
    if not is_manager(request.user) and task.assignee != request.user:
        messages.error(request, 'You cannot complete this task.')
        return redirect('task_list')
    
    task.status = 'completed'
    task.completed_at = timezone.now()
    task.save()
    
    messages.success(request, f'Task "{task.title}" marked as completed!')
    return redirect('task_list')
