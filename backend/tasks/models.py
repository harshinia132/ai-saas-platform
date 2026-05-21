from django.db import models
from django.conf import settings
from django.utils import timezone

class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    current_workflow_step = models.CharField(max_length=100, blank=True, default='Task Created')
    approval_status = models.CharField(max_length=20, blank=True, default='pending')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_tasks')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    review_comments = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_tasks')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    ai_priority_score = models.FloatField(default=0.0)
    ai_suggested_assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_suggested_tasks')
    ai_recommendations = models.JSONField(default=dict, blank=True)
    
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='tasks')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def can_approve(self, user):
        return user.role in ['manager', 'org_admin', 'super_admin']
    
    def approve(self, user):
        self.approval_status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.current_workflow_step = 'Approved'
        self.save()
    
    def reject(self, user, comments):
        self.approval_status = 'rejected'
        self.current_workflow_step = 'Rejected'
        self.review_comments = comments
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.save()
