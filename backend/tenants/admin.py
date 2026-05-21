from django.contrib import admin
from .models import Tenant

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'subdomain', 'plan', 'is_active')
    list_filter = ('plan', 'is_active')
    search_fields = ('name', 'subdomain')
