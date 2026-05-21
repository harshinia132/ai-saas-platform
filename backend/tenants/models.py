from django.db import models

class Tenant(models.Model):
    PLAN_CHOICES = (
        ('free', 'Free'),
        ('pro', 'Professional'),
        ('enterprise', 'Enterprise'),
    )
    
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=63, unique=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
