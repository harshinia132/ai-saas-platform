from django.contrib import admin
from django.urls import path, include
from home_views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ai-dashboard/', include('insights.urls')),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('workflow/', include('workflow.urls')),
    path('login/', include('accounts.urls')),  # This handles /login/
    path('logout/', include('accounts.urls')),  # This handles /logout/
    path('manager-dashboard/', include('accounts.urls')),  # This handles /manager-dashboard/
    path('employee-dashboard/', include('accounts.urls')),  # This handles /employee-dashboard/
    path('', home_view, name='home'),
    path('meeting-ai/', include('meeting_ai.urls')),
]
