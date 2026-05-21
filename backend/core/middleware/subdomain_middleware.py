from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse

class SubdomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host()
        subdomain = host.split('.')[0] if '.' in host and not host.startswith('www') else None
        
        if subdomain and subdomain not in ['localhost', '127.0.0.1', 'www', 'admin']:
            request.subdomain = subdomain
        else:
            request.subdomain = None
        
        return None
