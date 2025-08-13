"""
Admin para tenancy.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Tenant, Domain, TenantConfiguration

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin para Tenant."""
    
    list_display = [
        'name', 'cnpj', 'plan', 'billing_status', 'uf', 'municipio', 
        'is_active', 'created_at'
    ]
    list_filter = [
        'plan', 'billing_status', 'uf', 'is_active', 'lgpd_consent'
    ]
    search_fields = ['name', 'cnpj', 'razao_social', 'nome_fantasia']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'cnpj', 'razao_social', 'nome_fantasia')
        }),
        ('Segmentos', {
            'fields': ('cnae_principal', 'cnae_secundarios')
        }),
        ('Localização', {
            'fields': ('uf', 'municipio', 'cep', 'endereco')
        }),
        ('Configurações', {
            'fields': ('plan', 'billing_status', 'is_active')
        }),
        ('LGPD', {
            'fields': ('lgpd_consent', 'lgpd_consent_at', 'dpo_email')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filtra tenants por superusuário."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(users=request.user)

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """Admin para Domain."""
    
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['domain', 'tenant__name']

@admin.register(TenantConfiguration)
class TenantConfigurationAdmin(admin.ModelAdmin):
    """Admin para TenantConfiguration."""
    
    list_display = ['tenant', 'default_markup', 'risk_factor', 'email_notifications']
    list_filter = ['email_notifications', 'whatsapp_notifications', 'sms_notifications']
    search_fields = ['tenant__name']
    
    fieldsets = (
        ('Integrações', {
            'fields': ('enotas_api_key', 'nfeio_api_key')
        }),
        ('Notificações', {
            'fields': ('email_notifications', 'whatsapp_notifications', 'sms_notifications')
        }),
        ('Configurações de Negócio', {
            'fields': ('default_markup', 'risk_factor')
        }),
        ('Templates', {
            'fields': ('custom_templates',)
        }),
    )
