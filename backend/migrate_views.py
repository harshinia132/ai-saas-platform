from django.http import JsonResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def run_migrations(request):
    try:
        call_command('migrate', interactive=False)
        return JsonResponse({'status': 'success', 'message': 'Migrations completed'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def create_superuser(request):
    try:
        from users.models import User
        if not User.objects.filter(email='admin@example.com').exists():
            User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                full_name='Admin User',
                role='super_admin'
            )
        return JsonResponse({'status': 'success', 'message': 'Superuser created'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
