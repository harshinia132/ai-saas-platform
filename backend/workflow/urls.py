from django.urls import path
from . import views

urlpatterns = [
    path('', views.workflow_list, name='workflow_list'),
    path('create/', views.workflow_create, name='workflow_create'),
    path('builder/<int:instance_id>/', views.workflow_builder, name='workflow_builder'),
    path('start/<int:task_id>/', views.start_workflow, name='start_workflow'),
    path('<int:instance_id>/', views.workflow_detail, name='workflow_detail'),
]
