from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Workflow(models.Model):
    WORKFLOW_TYPES = (
        ('task', 'Task Workflow'),
        ('project', 'Project Workflow'),
        ('approval', 'Approval Workflow'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    workflow_type = models.CharField(max_length=20, choices=WORKFLOW_TYPES, default='task')
    is_active = models.BooleanField(default=True)
    steps = models.JSONField(default=list)
    
    avg_completion_time = models.FloatField(default=0.0)
    bottleneck_step_id = models.IntegerField(null=True, blank=True)
    optimization_suggestions = models.JSONField(default=dict, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_workflows')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_step_by_id(self, step_id):
        for step in self.steps:
            if step.get('id') == step_id:
                return step
        return None
    
    def get_first_step(self):
        for step in self.steps:
            if step.get('type') == 'start':
                return step
        return self.steps[0] if self.steps else None


class WorkflowInstance(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('timeout', 'Timeout'),
        ('failed', 'Failed'),
    )
    
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='instances')
    task = models.OneToOneField('tasks.Task', on_delete=models.CASCADE, related_name='workflow_instance')
    current_step_id = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    step_history = models.JSONField(default=list)
    context_data = models.JSONField(default=dict, blank=True)
    
    step_started_at = models.DateTimeField(null=True, blank=True)
    timeout_at = models.DateTimeField(null=True, blank=True)
    is_timeout_notified = models.BooleanField(default=False)
    
    predicted_completion_date = models.DateTimeField(null=True, blank=True)
    confidence_score = models.FloatField(default=0.0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.workflow.name} - {self.task.title}"
    
    def get_current_step(self):
        return self.workflow.get_step_by_id(self.current_step_id)
    
    def get_step_timeout_hours(self):
        current_step = self.get_current_step()
        return current_step.get('timeout_hours', 48)
    
    def set_timeout(self):
        timeout_hours = self.get_step_timeout_hours()
        self.timeout_at = timezone.now() + timedelta(hours=timeout_hours)
        self.save()
    
    def advance_to_next_step(self, user, comments=''):
        current_step = self.get_current_step()
        if not current_step:
            return False
        
        duration = 0
        if self.step_started_at:
            duration = (timezone.now() - self.step_started_at).total_seconds() / 3600
        
        self.step_history.append({
            'step_id': current_step['id'],
            'step_name': current_step['name'],
            'status': 'completed',
            'started_at': self.step_started_at.isoformat() if self.step_started_at else None,
            'completed_at': timezone.now().isoformat(),
            'duration_hours': duration,
            'completed_by': user.email,
            'comments': comments
        })
        
        next_step_id = current_step.get('next_step')
        if next_step_id:
            self.current_step_id = next_step_id
            self.step_started_at = timezone.now()
            self.set_timeout()
            next_step = self.workflow.get_step_by_id(next_step_id)
            
            if next_step and next_step.get('type') == 'end':
                self.status = 'completed'
                self.completed_at = timezone.now()
                self.task.status = 'completed'
                self.task.save()
        else:
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.task.status = 'completed'
            self.task.save()
        
        self.save()
        return True
    
    def reject_step(self, user, reason=''):
        current_step = self.get_current_step()
        reject_step_id = current_step.get('reject_step')
        
        if reject_step_id:
            self.current_step_id = reject_step_id
            self.status = 'rejected'
            self.step_history.append({
                'step_id': current_step['id'],
                'step_name': current_step['name'],
                'status': 'rejected',
                'completed_at': timezone.now().isoformat(),
                'completed_by': user.email,
                'comments': reason
            })
            self.step_started_at = timezone.now()
            self.set_timeout()
            self.save()
            return True
        return False
    
    def get_ai_suggested_assignee(self):
        from users.models import User
        current_step = self.get_current_step()
        required_role = current_step.get('required_role', 'employee')
        
        candidates = User.objects.filter(role=required_role, is_active=True)
        
        best_candidate = None
        lowest_workload = float('inf')
        
        for candidate in candidates:
            workload = candidate.assigned_tasks.filter(status__in=['todo', 'in_progress']).count()
            if workload < lowest_workload:
                lowest_workload = workload
                best_candidate = candidate
        
        return best_candidate
    
    def predict_completion_date(self):
        avg_time_per_step = self.workflow.avg_completion_time / max(len(self.workflow.steps), 1)
        remaining_steps = len([s for s in self.workflow.steps if s.get('id') >= self.current_step_id and s.get('type') != 'end'])
        estimated_hours = remaining_steps * avg_time_per_step if avg_time_per_step > 0 else 24
        
        self.predicted_completion_date = timezone.now() + timedelta(hours=estimated_hours)
        self.confidence_score = min(0.95, max(0.5, 1.0 - (remaining_steps * 0.1)))
        self.save()
        return self.predicted_completion_date
    
    def can_user_act(self, user):
        current_step = self.get_current_step()
        required_role = current_step.get('required_role', 'employee')
        
        role_permissions = {
            'employee': ['employee'],
            'manager': ['employee', 'manager'],
            'admin': ['employee', 'manager', 'org_admin', 'super_admin']
        }
        
        allowed_roles = role_permissions.get(required_role, ['employee'])
        return user.role in allowed_roles or user.is_superuser
