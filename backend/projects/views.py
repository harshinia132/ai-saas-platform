from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Project
from tasks.models import Task
from users.models import User

def is_manager(user):
    return user.role in ['manager', 'org_admin', 'super_admin'] or user.is_superuser

@login_required
def project_list(request):
    if is_manager(request.user):
        projects = Project.objects.all()
        can_edit = True
    else:
        projects = Project.objects.filter(team_members=request.user)
        can_edit = False
    
    context = {
        'projects': projects,
        'can_edit': can_edit,
        'is_manager': is_manager(request.user),
    }
    return render(request, 'projects/list.html', context)

@login_required
@user_passes_test(is_manager)
def project_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date') or None
        
        project = Project.objects.create(
            name=name,
            description=description,
            due_date=due_date if due_date else None,
            created_by=request.user,
            status='active'
        )
        messages.success(request, f'Project "{name}" created successfully!')
        return redirect('project_list')
    
    return render(request, 'projects/create.html')

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if not is_manager(request.user) and request.user not in project.team_members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('project_list')
    
    tasks = project.tasks.all()
    
    context = {
        'project': project,
        'tasks': tasks,
        'is_manager': is_manager(request.user),
    }
    return render(request, 'projects/detail.html', context)

@login_required
@user_passes_test(is_manager)
def project_edit(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        project.name = request.POST.get('name')
        project.description = request.POST.get('description')
        project.status = request.POST.get('status')
        
        # Handle empty date
        due_date = request.POST.get('due_date')
        if due_date and due_date.strip():
            project.due_date = due_date
        else:
            project.due_date = None
        
        project.save()
        messages.success(request, f'Project "{project.name}" updated successfully!')
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'projects/edit.html', {'project': project})

@login_required
@user_passes_test(is_manager)
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" deleted successfully!')
        return redirect('project_list')
    
    return render(request, 'projects/delete.html', {'project': project})
