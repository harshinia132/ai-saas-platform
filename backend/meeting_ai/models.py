from django.db import models
from django.conf import settings

class MeetingSummary(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    meeting_date = models.DateTimeField(auto_now_add=True)
    transcript = models.TextField()
    summary = models.TextField(blank=True)
    action_items = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
