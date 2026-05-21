from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
]
