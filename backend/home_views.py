from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home_view(request):
    if request.user.is_authenticated:
        if request.user.role in ['manager', 'org_admin', 'super_admin'] or request.user.is_superuser:
            return redirect('manager_dashboard')
        else:
            return redirect('employee_dashboard')
    
    tenant = getattr(request, 'tenant', None)
    subdomain = getattr(request, 'subdomain', None)
    
    context = {
        'tenant': tenant,
        'subdomain': subdomain,
    }
    return render(request, 'home.html', context)
