from django.db import models
from django.conf import settings

class Project(models.Model):
    STATUS_CHOICES = (
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    team_members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='assigned_projects')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name
