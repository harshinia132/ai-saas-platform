from django.utils.deprecation import MiddlewareMixin
from tenants.models import Tenant

class TenantIsolationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None
        
        host = request.get_host()
        subdomain = None
        
        if '.' in host:
            parts = host.split('.')
            if len(parts) >= 3:
                subdomain = parts[0]
            elif len(parts) == 2 and parts[0] not in ['localhost', '127.0.0.1', 'www']:
                subdomain = parts[0]
        
        if subdomain:
            try:
                tenant = Tenant.objects.filter(subdomain=subdomain, is_active=True).first()
                request.tenant = tenant if tenant else None
            except:
                request.tenant = None
        else:
            request.tenant = None
        
        return None
