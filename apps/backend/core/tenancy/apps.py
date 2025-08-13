"""
Configuração do app tenancy.
"""
from django.apps import AppConfig

class TenancyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.tenancy'
    verbose_name = 'Tenancy'
