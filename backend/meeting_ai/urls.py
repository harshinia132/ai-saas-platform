from django.urls import path
from . import views

urlpatterns = [
    path('', views.meeting_summarize, name='meeting_summarize'),
]
