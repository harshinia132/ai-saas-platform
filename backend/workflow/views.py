from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Workflow, WorkflowInstance
from tasks.models import Task
from users.models import User

def is_manager(user):
    return user.role in ['manager', 'org_admin', 'super_admin'] or user.is_superuser

@login_required
def workflow_list(request):
    workflows = Workflow.objects.filter(is_active=True)
    workflow_instances = WorkflowInstance.objects.filter(status__in=['pending', 'in_progress'])
    return render(request, 'workflow/list.html', {
        'workflows': workflows,
        'workflow_instances': workflow_instances
    })

@login_required
@user_passes_test(is_manager)
def workflow_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        workflow_type = request.POST.get('workflow_type')
        
        steps = [
            {'id': 1, 'name': 'Task Created', 'type': 'start', 'order': 1, 'next_step': 2},
            {'id': 2, 'name': 'Manager Approval', 'type': 'approval', 'order': 2, 'next_step': 3, 'reject_step': 1, 'required_role': 'manager', 'timeout_hours': 48},
            {'id': 3, 'name': 'Development', 'type': 'action', 'order': 3, 'next_step': 4, 'required_role': 'employee', 'timeout_hours': 72},
            {'id': 4, 'name': 'Code Review', 'type': 'review', 'order': 4, 'next_step': 5, 'required_role': 'manager', 'timeout_hours': 24},
            {'id': 5, 'name': 'Testing', 'type': 'action', 'order': 5, 'next_step': 6, 'required_role': 'employee', 'timeout_hours': 48},
            {'id': 6, 'name': 'Deployment', 'type': 'action', 'order': 6, 'next_step': 7, 'required_role': 'manager', 'timeout_hours': 24},
            {'id': 7, 'name': 'Completed', 'type': 'end', 'order': 7}
        ]
        
        workflow = Workflow.objects.create(
            name=name,
            description=description,
            workflow_type=workflow_type,
            steps=steps,
            created_by=request.user
        )
        messages.success(request, f'Workflow "{name}" created successfully!')
        return redirect('workflow_list')
    
    return render(request, 'workflow/create.html')

@login_required
def start_workflow(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    workflow = Workflow.objects.filter(workflow_type='task', is_active=True).first()
    
    if not workflow:
        messages.error(request, 'No workflow found. Please create a workflow first.')
        return redirect('task_detail', task_id=task.id)
    
    if hasattr(task, 'workflow_instance'):
        messages.warning(request, 'Workflow already started for this task.')
        return redirect('workflow_builder', instance_id=task.workflow_instance.id)
    
    workflow_instance = WorkflowInstance.objects.create(
        workflow=workflow,
        task=task,
        current_step_id=workflow.get_first_step()['id'],
        status='in_progress',
        step_started_at=timezone.now()
    )
    workflow_instance.set_timeout()
    
    messages.success(request, f'Workflow started for task: {task.title}')
    return redirect('workflow_builder', instance_id=workflow_instance.id)

@login_required
def workflow_builder(request, instance_id):
    instance = get_object_or_404(WorkflowInstance, id=instance_id)
    workflow = instance.workflow
    current_step = instance.get_current_step()
    can_act = instance.can_user_act(request.user)
    
    completed_step_ids = [h.get('step_id') for h in instance.step_history]
    
    bottleneck = None
    bottleneck_step = None
    suggested_assignee = instance.get_ai_suggested_assignee()
    match_score = 85 if suggested_assignee else 0
    
    predicted_date = instance.predicted_completion_date
    confidence_score = instance.confidence_score * 100 if instance.confidence_score else 0
    
    if not predicted_date and instance.step_started_at:
        instance.predict_completion_date()
        predicted_date = instance.predicted_completion_date
        confidence_score = instance.confidence_score * 100 if instance.confidence_score else 0
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action == 'approve' and can_act:
            instance.advance_to_next_step(request.user, comments)
            messages.success(request, f'Step "{current_step["name"]}" completed!')
            return redirect('workflow_builder', instance_id=instance.id)
        elif action == 'reject' and can_act:
            instance.reject_step(request.user, comments)
            messages.warning(request, f'Step "{current_step["name"]}" rejected!')
            return redirect('workflow_builder', instance_id=instance.id)
    
    context = {
        'workflow': workflow,
        'instance': instance,
        'current_step': current_step,
        'can_act': can_act,
        'completed_step_ids': completed_step_ids,
        'bottleneck': bottleneck,
        'bottleneck_step': bottleneck_step,
        'suggested_assignee': suggested_assignee,
        'match_score': match_score,
        'predicted_date': predicted_date,
        'confidence_score': confidence_score,
    }
    return render(request, 'workflow/builder.html', context)

@login_required
def workflow_detail(request, instance_id):
    return redirect('workflow_builder', instance_id=instance_id)
