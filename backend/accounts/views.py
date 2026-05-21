from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import User
from tasks.models import Task

def login_view(request):
    if request.user.is_authenticated:
        if request.user.role in ['manager', 'org_admin', 'super_admin'] or request.user.is_superuser:
            return redirect('manager_dashboard')
        else:
            return redirect('employee_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            try:
                user_obj = User.objects.get(email=email)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            display_name = user.full_name if hasattr(user, 'full_name') and user.full_name else user.email
            messages.success(request, f'Welcome back, {display_name}!')
            
            if user.role in ['manager', 'org_admin', 'super_admin'] or user.is_superuser:
                return redirect('manager_dashboard')
            else:
                return redirect('employee_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

@login_required
def manager_dashboard(request):
    from tasks.models import Task
    from projects.models import Project
    
    total_projects = Project.objects.count()
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='completed').count()
    
    display_name = request.user.full_name if hasattr(request.user, 'full_name') and request.user.full_name else request.user.email
    
    context = {
        'user': request.user,
        'display_name': display_name,
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'accounts/manager_dashboard.html', context)

@login_required
def employee_dashboard(request):
    my_tasks = Task.objects.filter(assignee=request.user).count()
    completed_tasks = Task.objects.filter(assignee=request.user, status='completed').count()
    assigned_tasks = Task.objects.filter(assignee=request.user)[:10]
    
    display_name = request.user.full_name if hasattr(request.user, 'full_name') and request.user.full_name else request.user.email
    
    insight = "Focus on high-priority tasks first for better productivity!"
    
    context = {
        'user': request.user,
        'display_name': display_name,
        'my_tasks': my_tasks,
        'completed_tasks': completed_tasks,
        'assigned_tasks': assigned_tasks,
        'insight': insight,
    }
    return render(request, 'accounts/employee_dashboard.html', context)
